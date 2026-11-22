"""
Build the canonical, cleaned text corpus → documents_clean.parquet + data_quality_report.md.

Inputs:  data/processed/news_raw.parquet, data/processed/reddit_posts_raw.parquet
Outputs: data/processed/documents_clean.parquet, data/processed/data_quality_report.md

Usage:
  PYTHONPATH=. python src/cleaning/pipeline.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.cleaning.documents import (
    DOCUMENT_COLUMNS,
    news_to_documents,
    reddit_to_documents,
)
from src.cleaning.language import detect_language
from src.cleaning.text import text_hash
from src.utils.paths import (
    CONFIGS_DIR,
    DATA_QUALITY_REPORT_PATH,
    DOCUMENTS_CLEAN_PARQUET,
    MARKET_DAILY_PATH,
    NEWS_RAW_PARQUET,
    REDDIT_POSTS_RAW_PARQUET,
    ensure_data_dirs,
)

SOURCE_TYPES = ("news", "reddit")


def load_cleaning_config(path: Path | None = None) -> dict:
    cfg_path = path or (CONFIGS_DIR / "cleaning.yaml")
    with open(cfg_path) as f:
        return yaml.safe_load(f)


@dataclass
class Funnel:
    """Row counts removed per cleaning step, per source_type, plus audit examples."""

    steps: list[tuple[str, dict[str, int]]] = field(default_factory=list)
    examples: dict[str, list[str]] = field(default_factory=dict)

    def record(self, step: str, dropped: pd.DataFrame, *, example_col: str | None = None) -> None:
        counts = {st: int((dropped["source_type"] == st).sum()) for st in SOURCE_TYPES}
        self.steps.append((step, counts))
        if example_col and len(dropped):
            sample = dropped[example_col].dropna().astype(str)
            self.examples[step] = sample.drop_duplicates().head(8).str.slice(0, 120).tolist()


def _drop(df: pd.DataFrame, mask: pd.Series, step: str, funnel: Funnel, example_col=None):
    mask = mask.fillna(False).astype(bool)
    funnel.record(step, df.loc[mask], example_col=example_col)
    return df.loc[~mask]


# ---------------------------------------------------------------------------
# Reddit platform filters (applied to raw posts, before text cleaning)
# ---------------------------------------------------------------------------


def filter_reddit_posts(posts: pd.DataFrame, cfg: dict, funnel: Funnel) -> pd.DataFrame:
    rcfg = cfg.get("reddit") or {}
    df = posts.assign(source_type="reddit")

    removed = set(rcfg.get("drop_removed_categories") or [])
    df = _drop(
        df, df["removed_by_category"].isin(removed), "reddit: removed / deleted post", funnel,
        example_col="title",
    )
    if rcfg.get("drop_stickied", True):
        df = _drop(df, df["stickied"], "reddit: stickied (pinned) post", funnel, example_col="title")
    if rcfg.get("drop_distinguished", True):
        df = _drop(
            df, df["distinguished"].isin(["moderator", "admin"]),
            "reddit: moderator/admin post", funnel, example_col="title",
        )
    bots = {b.lower() for b in rcfg.get("bot_authors") or []}
    df = _drop(
        df, df["author"].fillna("").str.lower().isin(bots), "reddit: bot author", funnel,
        example_col="title",
    )
    patterns = rcfg.get("megathread_title_patterns") or []
    if patterns:
        mega = re.compile("|".join(f"(?:{p})" for p in patterns), re.I)
        is_mega = df["title"].fillna("").map(lambda t: bool(mega.search(t)))
        df = _drop(df, is_mega, "reddit: megathread / recurring thread", funnel, example_col="title")
    if rcfg.get("drop_over_18", False):
        df = _drop(df, df["over_18"], "reddit: NSFW", funnel, example_col="title")
    return df.drop(columns="source_type")


# ---------------------------------------------------------------------------
# Document-level filters
# ---------------------------------------------------------------------------


def dedupe_documents(docs: pd.DataFrame, window_hours: float, funnel: Funnel) -> pd.DataFrame:
    """
    1. Exact doc_id duplicates.
    2. Same normalized-text hash within one source_type, reappearing within
       `window_hours` of the previous copy (earliest copy kept, since first
       appearance is what matters for timing).
    """
    docs = docs.sort_values(["timestamp_utc", "doc_id"], kind="stable")
    docs = _drop(docs, docs.duplicated("doc_id", keep="first"), "dedup: exact doc_id", funnel)

    docs = docs.sort_values(["source_type", "text_hash", "timestamp_utc", "doc_id"], kind="stable")
    same_group = (docs["source_type"] == docs["source_type"].shift()) & (
        docs["text_hash"] == docs["text_hash"].shift()
    )
    gap = docs["timestamp_utc"] - docs["timestamp_utc"].shift()
    is_dup = same_group & (gap <= pd.Timedelta(hours=window_hours))
    return _drop(
        docs, is_dup, f"dedup: same text within {window_hours:g}h (hash)", funnel,
        example_col="headline",
    )


def _min_words(cfg: dict) -> dict[str, int]:
    """Per-source_type minimum word counts; a bare int applies to every source."""
    raw = cfg.get("min_words", 5)
    if isinstance(raw, dict):
        return {st: int(raw.get(st, 0)) for st in SOURCE_TYPES}
    return {st: int(raw) for st in SOURCE_TYPES}


# ---------------------------------------------------------------------------
# Time alignment
# ---------------------------------------------------------------------------


def _minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def load_yield_dates(series: str, path: Path = MARKET_DAILY_PATH) -> np.ndarray | None:
    """Sorted dates with a non-null observation of `series` in market_daily.csv."""
    if not path.exists():
        return None
    market = pd.read_csv(path, parse_dates=["date"])
    if series not in market.columns:
        return None
    dates = market.loc[market[series].notna(), "date"].sort_values()
    return dates.to_numpy(dtype="datetime64[ns]")


def add_time_alignment(
    docs: pd.DataFrame, cfg: dict, market_path: Path = MARKET_DAILY_PATH
) -> pd.DataFrame:
    tcfg = cfg.get("time_alignment") or {}
    tz = tcfg.get("timezone", "America/New_York")
    open_m = _minutes(tcfg.get("session_open", "09:30"))
    close_m = _minutes(tcfg.get("session_close", "16:00"))
    cutoff_m = _minutes(tcfg.get("yield_cutoff", "15:30"))

    out = docs.copy()
    et = out["timestamp_utc"].dt.tz_convert(tz)
    out["timestamp_et"] = et
    out["et_date"] = et.dt.tz_localize(None).dt.normalize().astype("datetime64[us]")

    minute_of_day = et.dt.hour * 60 + et.dt.minute
    at_midnight = (et.dt.hour == 0) & (et.dt.minute == 0) & (et.dt.second == 0)
    # Only news carries date-only stamps (Fed archive items stored at 00:00 ET);
    # Reddit times are exact to the second.
    out["timestamp_is_date_only"] = (out["source_type"] == "news") & at_midnight

    session = np.select(
        [minute_of_day < open_m, minute_of_day < close_m],
        ["pre", "regular"],
        default="post",
    )
    session = np.where(et.dt.dayofweek >= 5, "weekend", session)
    session = np.where(out["timestamp_is_date_only"], "date_only", session)
    out["market_session"] = session

    # First daily yield observation that can reflect the document
    candidate = out["et_date"] + pd.to_timedelta((minute_of_day >= cutoff_m).astype(int), unit="D")
    valid = load_yield_dates(tcfg.get("yield_series", "DGS10"), market_path)
    if valid is None or len(valid) == 0:
        print("[align] market_daily.csv / yield series missing; yield_date left null")
        out["yield_date"] = pd.NaT
    else:
        cand = candidate.to_numpy(dtype="datetime64[ns]")
        idx = np.searchsorted(valid, cand, side="left")
        found = idx < len(valid)
        yd = np.full(len(out), np.datetime64("NaT", "ns"))
        yd[found] = valid[idx[found]]
        out["yield_date"] = pd.to_datetime(yd).astype("datetime64[us]")
        out.loc[out["timestamp_utc"].isna(), "yield_date"] = pd.NaT
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class CleanResult:
    docs: pd.DataFrame
    funnel: Funnel
    input_counts: dict[str, int]
    language_drops: dict[str, int]


def build_documents(
    cfg: dict,
    news: pd.DataFrame | None,
    posts: pd.DataFrame | None,
    market_path: Path = MARKET_DAILY_PATH,
) -> CleanResult:
    funnel = Funnel()
    input_counts = {
        "news": 0 if news is None else len(news),
        "reddit": 0 if posts is None else len(posts),
    }

    frames = []
    if news is not None and len(news):
        frames.append(news_to_documents(news))
    if posts is not None and len(posts):
        posts = filter_reddit_posts(posts, cfg, funnel)
        frames.append(reddit_to_documents(posts))
    if not frames:
        raise SystemExit("No inputs found: run the news and/or reddit pipelines first.")
    docs = pd.concat(frames, ignore_index=True)

    docs = _drop(docs, docs["timestamp_utc"].isna(), "missing / unparseable timestamp", funnel,
                 example_col="headline")
    if cfg.get("start_date"):
        start = pd.Timestamp(cfg["start_date"], tz="UTC")
        docs = _drop(docs, docs["timestamp_utc"] < start, "before start_date", funnel)
    if cfg.get("end_date"):
        end = pd.Timestamp(cfg["end_date"], tz="UTC")
        docs = _drop(docs, docs["timestamp_utc"] >= end, "on/after end_date", funnel)

    docs["n_words"] = docs["text"].str.split().str.len().fillna(0).astype("int64")
    docs = _drop(docs, docs["n_words"] == 0, "empty text", funnel)
    min_words = _min_words(cfg)
    threshold = docs["source_type"].map(min_words).fillna(0)
    label = ", ".join(f"{st} < {n}" for st, n in min_words.items())
    docs = _drop(docs, docs["n_words"] < threshold, f"short text ({label} words)", funnel,
                 example_col="text")

    lcfg = cfg.get("language") or {}
    lang = docs["text"].map(
        lambda t: detect_language(
            t,
            min_latin_share=float(lcfg.get("min_latin_share", 0.6)),
            min_foreign_hits=int(lcfg.get("min_foreign_hits", 3)),
        )
    )
    language_drops = lang[lang != "en"].value_counts().to_dict()
    docs = _drop(docs, lang != "en", "non-English", funnel, example_col="headline")

    docs["text_hash"] = docs["text"].map(text_hash)
    window = float((cfg.get("dedup") or {}).get("window_hours", 24))
    docs = dedupe_documents(docs, window, funnel)

    docs = add_time_alignment(docs, cfg, market_path)
    docs = docs.sort_values(["timestamp_utc", "doc_id"], kind="stable").reset_index(drop=True)
    return CleanResult(docs[DOCUMENT_COLUMNS], funnel, input_counts, language_drops)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def _md_table(headers: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return out


def _fmt(n) -> str:
    return f"{int(n):,}"


def write_quality_report(result: CleanResult, cfg: dict, path: Path = DATA_QUALITY_REPORT_PATH) -> Path:
    docs = result.docs
    funnel = result.funnel
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out_counts = docs["source_type"].value_counts().to_dict()

    lines = [
        "# Data Quality Report — documents_clean.parquet",
        "",
        f"- **Generated:** {now} by `src/cleaning/pipeline.py`",
        "- **Inputs:** `data/processed/news_raw.parquet`, `data/processed/reddit_posts_raw.parquet`",
        "- **Output:** `data/processed/documents_clean.parquet`",
        "- **Config:** `configs/cleaning.yaml`",
        "",
        "## Summary",
        "",
    ]
    rows = []
    for st in SOURCE_TYPES:
        n_in = result.input_counts.get(st, 0)
        n_out = out_counts.get(st, 0)
        kept = f"{n_out / n_in:.1%}" if n_in else "—"
        rows.append([st, _fmt(n_in), _fmt(n_out), kept])
    tot_in = sum(result.input_counts.values())
    rows.append(["**total**", _fmt(tot_in), _fmt(len(docs)), f"{len(docs) / tot_in:.1%}" if tot_in else "—"])
    lines += _md_table(["source_type", "raw rows", "clean docs", "kept"], rows)

    # Funnel
    lines += ["", "## Cleaning funnel (rows dropped per step, in order)", ""]
    remaining = dict(result.input_counts)
    rows = []
    for step, counts in funnel.steps:
        for st in SOURCE_TYPES:
            remaining[st] -= counts[st]
        rows.append([step, _fmt(counts["news"]), _fmt(counts["reddit"]),
                     _fmt(remaining["news"]), _fmt(remaining["reddit"])])
    lines += _md_table(
        ["step", "news dropped", "reddit dropped", "news remaining", "reddit remaining"], rows
    )
    if result.language_drops:
        langs = ", ".join(f"`{k}`: {v:,}" for k, v in sorted(result.language_drops.items(), key=lambda x: -x[1]))
        lines += ["", f"Non-English drops by detected language: {langs}."]

    # Composition
    lines += ["", "## Clean documents by source", ""]
    by_src = (
        docs.groupby(["source_type", "source_name"])
        .agg(
            docs=("doc_id", "size"),
            with_body=("body", lambda s: int(s.notna().sum())),
            median_words=("n_words", "median"),
            first=("timestamp_utc", "min"),
            last=("timestamp_utc", "max"),
        )
        .reset_index()
        .sort_values(["source_type", "docs"], ascending=[True, False])
    )
    lines += _md_table(
        ["source_type", "source_name", "docs", "with body", "median words", "first", "last"],
        [
            [r.source_type, r.source_name, _fmt(r.docs), _fmt(r.with_body), f"{r.median_words:.0f}",
             f"{r.first:%Y-%m-%d}", f"{r.last:%Y-%m-%d}"]
            for r in by_src.itertuples()
        ],
    )

    # Length
    lines += ["", "## Text length (words)", ""]
    rows = []
    for st, g in docs.groupby("source_type"):
        q = g["n_words"].quantile([0.1, 0.5, 0.9, 0.99])
        rows.append([st, f"{q[0.1]:.0f}", f"{q[0.5]:.0f}", f"{q[0.9]:.0f}", f"{q[0.99]:.0f}",
                     f"{g['body'].notna().mean():.1%}"])
    lines += _md_table(["source_type", "p10", "median", "p90", "p99", "share with body"], rows)

    # Coverage
    lines += ["", "## Time coverage", ""]
    ranges = docs.groupby("source_type")["timestamp_utc"].agg(["min", "max"])
    for st, r in ranges.iterrows():
        lines.append(f"- **{st}:** {r['min']:%Y-%m-%d %H:%M} → {r['max']:%Y-%m-%d %H:%M} UTC")
    if {"news", "reddit"}.issubset(ranges.index):
        lo = max(ranges.loc["news", "min"], ranges.loc["reddit", "min"])
        hi = min(ranges.loc["news", "max"], ranges.loc["reddit", "max"])
        if lo < hi:
            in_overlap = docs[(docs["timestamp_utc"] >= lo) & (docs["timestamp_utc"] <= hi)]
            oc = in_overlap["source_type"].value_counts()
            lines.append(
                f"- **Overlap (both sources present):** {lo:%Y-%m-%d} → {hi:%Y-%m-%d} — "
                f"news {oc.get('news', 0):,} docs, reddit {oc.get('reddit', 0):,} docs"
            )
        else:
            lines.append("- **Overlap:** none — news and reddit samples do not overlap in time")

    monthly = (
        docs.assign(month=docs["timestamp_et"].dt.strftime("%Y-%m"))
        .pivot_table(index="month", columns="source_type", values="doc_id", aggfunc="size", fill_value=0)
        .sort_index()
        .tail(24)
    )
    lines += ["", "Documents per month (last 24 months, ET):", ""]
    cols = [c for c in SOURCE_TYPES if c in monthly.columns]
    lines += _md_table(["month"] + cols, [[m] + [_fmt(monthly.loc[m, c]) for c in cols] for m in monthly.index])

    # Timestamps
    tcfg = cfg.get("time_alignment") or {}
    lines += ["", "## Timestamp quality and alignment", ""]
    n_date_only = int(docs["timestamp_is_date_only"].sum())
    lines.append(
        f"- **Date-only timestamps:** {n_date_only:,} docs (news items stamped 00:00 ET with no "
        "time of day). Use them only for daily analysis; exclude from intraday windows."
    )
    lines.append(f"- **yield_date null:** {int(docs['yield_date'].isna().sum()):,} docs "
                 "(after the last available yield observation in market_daily.csv).")
    sess = pd.crosstab(docs["market_session"], docs["source_type"])
    lines += ["", "Market session (ET; `regular` = "
              f"{tcfg.get('session_open', '09:30')}–{tcfg.get('session_close', '16:00')} weekdays, holidays not excluded):", ""]
    lines += _md_table(["market_session"] + list(sess.columns),
                       [[i] + [_fmt(v) for v in r] for i, r in sess.iterrows()])

    # Examples
    if funnel.examples:
        lines += ["", "## Examples of dropped rows (for auditing filters)", ""]
        for step, ex in funnel.examples.items():
            lines.append(f"**{step}**")
            lines.append("")
            for e in ex:
                lines.append(f"- {e.replace(chr(10), ' ').replace('|', '/')}")
            lines.append("")

    # Rules + dictionary
    rcfg = cfg.get("reddit") or {}
    lines += [
        "## Cleaning rules",
        "",
        "1. **Reddit platform filters** (raw posts): drop `removed_by_category` in "
        f"{', '.join(f'`{c}`' for c in rcfg.get('drop_removed_categories') or [])}; "
        "stickied posts; moderator/admin-distinguished posts; bot authors "
        f"({', '.join(rcfg.get('bot_authors') or [])}); titles matching megathread patterns. "
        "Posts by deleted accounts are kept when the post text itself survives.",
        "2. **Text normalization:** HTML → text, entity unescaping, Unicode NFKC, zero-width "
        "characters removed, URLs removed, Reddit markdown stripped, boilerplate lines removed "
        "(e.g. *For media inquiries…*, *For release at…*, *Continue reading…*, bare datelines), "
        "whitespace collapsed. Google News titles have the ` - Publisher` suffix moved to "
        "`meta.publisher`. Bodies that only repeat the headline are dropped (`body` = null).",
        "3. **Timezone:** all timestamps parsed as UTC (`timestamp_utc`), converted to "
        f"{tcfg.get('timezone', 'America/New_York')} for `timestamp_et` / `et_date` / `market_session`.",
        "4. **Missing timestamp:** dropped (cannot be aligned to market data; collection time "
        "is not used as a substitute because it is not the publication time).",
        "5. **Empty / short:** dropped when `text` has fewer than "
        + ", ".join(f"{n} words ({st})" for st, n in _min_words(cfg).items()) + ".",
        "6. **Language:** English only (script check + stopword-ratio heuristic, `src/cleaning/language.py`).",
        "7. **Dedup:** exact `doc_id`, then identical normalized text (`text_hash`) within the same "
        f"source_type reappearing within {(cfg.get('dedup') or {}).get('window_hours', 24)}h of the "
        "previous copy; the earliest copy is kept.",
        "",
        "## Column dictionary",
        "",
        "| Column | Description |",
        "|--------|-------------|",
        "| doc_id | `news:<article_id>` or `reddit:<post_id>`; unique |",
        "| source_type | `news` or `reddit` |",
        "| source_name | Publisher label (`cnbc`, `federal_reserve`, `google_news`, …) or `r/<subreddit>` |",
        "| timestamp_utc | Publication / post time, UTC |",
        "| headline | Cleaned headline / post title |",
        "| body | Cleaned body / selftext; null when absent or redundant with headline |",
        "| text | `headline` + blank line + `body` — the field to feed NLP models |",
        "| meta | JSON string of source fields (news: article_id, url, section, tag, ingest_method, "
        "publisher, collected_at_utc; reddit: post_id, subreddit, author, score, upvote_ratio, "
        "num_comments, permalink, url, domain, is_self, link_flair_text, over_18, crosspost_parent, "
        "ingest_method, score_observed_at_utc). Flatten with `src.cleaning.documents.expand_meta`. |",
        "| timestamp_et | `timestamp_utc` in America/New_York |",
        "| et_date | Calendar date in ET (naive, midnight) — joins to `market_daily.csv` `date` |",
        "| market_session | `pre` / `regular` / `post` / `weekend` (ET), or `date_only` |",
        f"| yield_date | First `{tcfg.get('yield_series', 'DGS10')}` observation date that can reflect "
        f"the doc: same ET date if before {tcfg.get('yield_cutoff', '15:30')} ET (CMT yields are "
        "fixed from ~3:30 p.m. bid quotes), else the next date with an observation (skips weekends "
        "and holidays). Join on `market_daily.csv` `date` for daily regressions |",
        "| timestamp_is_date_only | True when the source only provided a date (00:00 ET) |",
        "| n_words | Whitespace token count of `text` |",
        "| text_hash | SHA-256 (32 hex) of normalized `text`; used for dedup |",
        "",
        "## Known limitations",
        "",
        "- Reddit `score` / `num_comments` are archive snapshots taken shortly after posting "
        "(`meta.score_observed_at_utc`) and understate final engagement.",
        "- Language detection is heuristic; very short ticker-heavy posts default to English.",
        "- `market_session` ignores exchange holidays and early closes; `yield_date` handles "
        "holidays via the actual yield observation calendar.",
        "- News coverage is uneven over time (Fed archive is multi-year; RSS / Google News are recent), "
        "so compare news vs. Reddit inside the overlap window.",
        "",
    ]
    path.write_text("\n".join(lines))
    return path


def main() -> None:
    ensure_data_dirs()
    cfg = load_cleaning_config()
    news = pd.read_parquet(NEWS_RAW_PARQUET) if NEWS_RAW_PARQUET.exists() else None
    posts = pd.read_parquet(REDDIT_POSTS_RAW_PARQUET) if REDDIT_POSTS_RAW_PARQUET.exists() else None
    for name, df, p in (("news", news, NEWS_RAW_PARQUET), ("reddit", posts, REDDIT_POSTS_RAW_PARQUET)):
        print(f"{name}: {len(df):,} rows" if df is not None else f"{name}: missing ({p})")

    result = build_documents(cfg, news, posts)
    for step, counts in result.funnel.steps:
        print(f"  {step}: -{counts['news']:,} news, -{counts['reddit']:,} reddit")

    result.docs.to_parquet(DOCUMENTS_CLEAN_PARQUET, index=False)
    write_quality_report(result, cfg)
    print(f"Wrote {DOCUMENTS_CLEAN_PARQUET} ({len(result.docs):,} docs)")
    print(f"Wrote {DATA_QUALITY_REPORT_PATH}")
    print(result.docs["source_name"].value_counts().head(15))


if __name__ == "__main__":
    main()
