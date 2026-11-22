"""
Aggregate document scores into time-series factors (week 12).

Daily features are keyed on `yield_date` — the first DGS10 observation each
document can affect (see data_quality_report.md) — so they join directly to
market_daily.csv on `date` with no look-ahead.

Intraday features bucket exact timestamps (date-only news excluded) at 5-minute
and 30-minute frequencies; bucket labels are the bucket START in UTC.

Usage:
  PYTHONPATH=. python src/features/pipeline.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.utils.paths import (
    CONFIGS_DIR,
    DOCUMENTS_SCORED_PARQUET,
    FEATURES_DAILY_PARQUET,
    FEATURES_DICT_PATH,
    FEATURES_INTRADAY_PARQUET,
    MARKET_DAILY_PATH,
    ensure_data_dirs,
)

SOURCES = ("news", "reddit")


def load_features_config(path: Path | None = None) -> dict:
    with open(path or (CONFIGS_DIR / "features.yaml")) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Per-document weights and values
# ---------------------------------------------------------------------------


def document_weights(docs: pd.DataFrame, cfg: dict) -> pd.Series:
    """News: source-quality weight. Reddit: 1 + log1p(max(score, 0))."""
    meta = docs["meta"].map(json.loads)
    ncfg = cfg.get("news_weights") or {}
    default = float(ncfg.get("default_weight", 0.5))
    by_source = {k: float(v) for k, v in (ncfg.get("sources") or {}).items()}
    by_pub = {k.lower(): float(v) for k, v in (ncfg.get("google_news_publishers") or {}).items()}

    def news_weight(source: str, m: dict) -> float:
        if source == "google_news":
            return by_pub.get(str(m.get("publisher") or "").lower(), default)
        return by_source.get(source, default)

    w = pd.Series(np.nan, index=docs.index, dtype="float64")
    is_news = docs["source_type"] == "news"
    w[is_news] = [news_weight(s, m) for s, m in zip(docs.loc[is_news, "source_name"], meta[is_news])]
    is_reddit = docs["source_type"] == "reddit"
    score = pd.to_numeric(meta[is_reddit].map(lambda m: m.get("score")), errors="coerce").fillna(0)
    w[is_reddit] = 1.0 + np.log1p(score.clip(lower=0))
    return w


def prepare(docs: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    model = cfg.get("sentiment_model", "finbert")
    out = pd.DataFrame(index=docs.index)
    out["source_type"] = docs["source_type"]
    out["yield_date"] = docs["yield_date"]
    out["timestamp_utc"] = docs["timestamp_utc"]
    out["date_only"] = docs["timestamp_is_date_only"]
    out["relevant"] = docs["is_relevant"]
    out["w"] = document_weights(docs, cfg)
    out["sent"] = docs[f"{model}_sentiment_score"]
    out["vader"] = docs["vader_sentiment_score"]
    # Yield direction only on relevant docs: irrelevant chatter is not a rates signal
    out["ydir"] = docs["yield_direction_signal"].where(docs["is_relevant"])
    out["neg_spike"] = (out["sent"] <= float(cfg.get("negative_spike_threshold", -0.5))).astype(int)
    for col in [c for c in docs.columns if c.startswith("topic_")]:
        out[col] = docs[col]
    return out


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _wmean(values: pd.Series, weights: pd.Series, keys: list[pd.Series]) -> pd.Series:
    ok = values.notna() & weights.notna()
    num = (values[ok] * weights[ok]).groupby([k[ok] for k in keys]).sum()
    den = weights[ok].groupby([k[ok] for k in keys]).sum()
    return num / den


def aggregate(prep: pd.DataFrame, key: str, cfg: dict) -> pd.DataFrame:
    """One row per `key` value with per-source and topic aggregates."""
    topics = [c.removeprefix("topic_") for c in prep.columns if c.startswith("topic_")]
    cols: dict[str, pd.Series] = {}
    for st in SOURCES:
        d = prep[prep["source_type"] == st]
        g = d.groupby(key)
        cols[f"n_{st}"] = g.size()
        cols[f"n_{st}_relevant"] = g["relevant"].sum()
        cols[f"{st}_sent_n"] = g["sent"].count()
        cols[f"{st}_sent_mean"] = g["sent"].mean()
        cols[f"{st}_sent_wmean"] = _wmean(d["sent"], d["w"], [d[key]])
        cols[f"{st}_vader_mean"] = g["vader"].mean()
        cols[f"{st}_ydir_mean"] = g["ydir"].mean()
        cols[f"{st}_ydir_wmean"] = _wmean(d["ydir"], d["w"], [d[key]])
        cols[f"{st}_neg_spike"] = g["neg_spike"].sum()
        for t in cfg.get("topic_features") or []:
            if f"topic_{t}" not in d.columns:
                continue
            dt = d[d[f"topic_{t}"]]
            cols[f"{st}_{t}_sent_mean"] = dt.groupby(key)["sent"].mean()
            cols[f"{st}_{t}_ydir_mean"] = dt.groupby(key)["ydir"].mean()
    for t in topics:
        cols[f"n_topic_{t}"] = prep[prep[f"topic_{t}"]].groupby(key).size()
    out = pd.DataFrame(cols)
    count_cols = [c for c in out.columns if c.startswith("n_") or c.endswith(("_neg_spike", "_sent_n"))]
    out[count_cols] = out[count_cols].fillna(0).astype("int64")
    return out


def add_surprise(df: pd.DataFrame, cols: list[str], window: int, min_periods: int) -> pd.DataFrame:
    """z = (x_t − mean(x_{t−window..t−1})) / std(...): uses only prior periods."""
    out = df.copy()
    for c in cols:
        prior = out[c].shift(1).rolling(window, min_periods=min_periods)
        std = prior.std()
        out[f"{c}_z{window}"] = (out[c] - prior.mean()) / std.where(std > 0)
    return out


# ---------------------------------------------------------------------------
# Daily
# ---------------------------------------------------------------------------


def trading_calendar(series: str = "DGS10", path: Path = MARKET_DAILY_PATH) -> pd.DatetimeIndex:
    market = pd.read_csv(path, parse_dates=["date"])
    return pd.DatetimeIndex(market.loc[market[series].notna(), "date"]).sort_values()


def build_daily(prep: pd.DataFrame, cfg: dict, market_path: Path = MARKET_DAILY_PATH) -> pd.DataFrame:
    d = prep[prep["yield_date"].notna()]
    daily = aggregate(d, "yield_date", cfg)
    cal = trading_calendar(path=market_path)
    cal = cal[(cal >= daily.index.min()) & (cal <= daily.index.max())]
    daily = daily.reindex(cal.astype(daily.index.dtype))
    count_cols = [c for c in daily.columns if c.startswith("n_") or c.endswith(("_neg_spike", "_sent_n"))]
    daily[count_cols] = daily[count_cols].fillna(0).astype("int64")
    daily.index.name = "date"
    z_cols = [f"{st}_{m}" for st in SOURCES for m in ("sent_mean", "sent_wmean", "ydir_mean", "ydir_wmean")]
    z_cols += [f"n_{st}" for st in SOURCES]
    daily = add_surprise(
        daily, [c for c in z_cols if c in daily.columns],
        int(cfg.get("rolling_window", 30)), int(cfg.get("rolling_min_periods", 10)),
    )
    return daily.reset_index()


# ---------------------------------------------------------------------------
# Intraday
# ---------------------------------------------------------------------------


def build_intraday(prep: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    icfg = cfg.get("intraday") or {}
    start = pd.Timestamp(icfg.get("start_date", "2025-01-01"), tz="UTC")
    d = prep[(~prep["date_only"]) & (prep["timestamp_utc"] >= start)].copy()
    frames = []
    for freq in icfg.get("frequencies") or ["5min", "30min"]:
        d["bucket"] = d["timestamp_utc"].dt.floor(freq)
        agg = aggregate(d, "bucket", cfg)
        grid = pd.date_range(d["bucket"].min(), d["bucket"].max(), freq=freq, tz="UTC")
        agg = agg.reindex(grid.astype(agg.index.dtype))
        count_cols = [c for c in agg.columns if c.startswith("n_") or c.endswith(("_neg_spike", "_sent_n"))]
        agg[count_cols] = agg[count_cols].fillna(0).astype("int64")
        agg.index.name = "bucket_start_utc"

        # Volume shock: total docs vs trailing lookback (prior buckets only)
        n_prior = int(pd.Timedelta(icfg.get("shock_lookback", "24h")) / pd.Timedelta(freq))
        total = agg["n_news"] + agg["n_reddit"]
        prior = total.shift(1).rolling(n_prior, min_periods=max(2, n_prior // 4))
        std = prior.std()
        agg["shock_score"] = (total - prior.mean()) / std.where(std > 0)
        # Signed yield-direction pressure: sum of weighted signals in the bucket
        dd = d[d["ydir"].notna()]
        agg["ydir_pressure"] = (dd["ydir"] * dd["w"]).groupby(dd["bucket"]).sum().reindex(agg.index).fillna(0.0)
        agg.insert(0, "bucket_freq", freq)
        frames.append(agg.reset_index())
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Dictionary
# ---------------------------------------------------------------------------


def write_dictionary(daily: pd.DataFrame, intraday: pd.DataFrame, cfg: dict) -> Path:
    model = cfg.get("sentiment_model", "finbert")
    w = cfg.get("rolling_window", 30)
    lines = [
        "# Sentiment Feature Dictionary",
        "",
        f"- **features_daily.parquet:** {len(daily):,} trading days "
        f"({daily['date'].min():%Y-%m-%d} → {daily['date'].max():%Y-%m-%d}), {daily.shape[1]} columns",
        f"- **features_intraday.parquet:** {len(intraday):,} buckets "
        f"({', '.join(intraday['bucket_freq'].unique())}), {intraday.shape[1]} columns",
        "- Built by `src/features/pipeline.py` from `documents_scored.parquet`; config `configs/features.yaml`.",
        "",
        "## Keys and timing",
        "",
        "- **Daily `date`** = `yield_date`: the first DGS10 observation a document can affect "
        "(same ET day if before 15:30 ET, else next trading day). Join to `market_daily.csv` on `date`. "
        "Days with no documents have zero counts and null means.",
        "- **Intraday `bucket_start_utc`** = bucket start (UTC); `bucket_freq` is `5min` or `30min`. "
        "Date-only news timestamps are excluded; intraday starts "
        f"{(cfg.get('intraday') or {}).get('start_date')}.",
        "",
        "## Columns (`<src>` = `news` or `reddit`)",
        "",
        "| Column | Description |",
        "|---|---|",
        "| `n_<src>` | Documents in the period |",
        "| `n_<src>_relevant` | Of those, `is_relevant` (news, macro topic, or yield cue) |",
        f"| `<src>_sent_n` | Docs with a {model} score (relevant docs only) |",
        f"| `<src>_sent_mean` | Mean {model} `sentiment_score` (p_pos − p_neg) |",
        f"| `<src>_sent_wmean` | Weighted mean {model} score: news by source quality, Reddit by 1 + log1p(score) |",
        "| `<src>_vader_mean` | Mean VADER score over all docs (baseline) |",
        "| `<src>_ydir_mean` / `_ydir_wmean` | Mean / weighted `yield_direction_signal` over relevant docs (+ = yields up) |",
        f"| `<src>_neg_spike` | Docs with {model} score ≤ {cfg.get('negative_spike_threshold')} |",
        "| `<src>_<topic>_sent_mean` | Mean tone of docs tagged with the topic |",
        "| `<src>_<topic>_ydir_mean` | Mean yield-direction signal of docs tagged with the topic |",
        "| `n_topic_<topic>` | Docs (both sources) tagged with the topic |",
        f"| `*_z{w}` (daily) | Surprise: (x − trailing {w}-day mean) / trailing std, prior days only |",
        "| `shock_score` (intraday) | Doc-volume z-score vs the prior "
        f"{(cfg.get('intraday') or {}).get('shock_lookback')} of buckets |",
        "| `ydir_pressure` (intraday) | Σ weight × yield_direction_signal in the bucket (signed) |",
        "",
        "## Caveats",
        "",
        f"- {model} covers relevant documents only; `*_sent_*` features are null on days with no scored docs.",
        "- `growth` topic features double as recession sentiment (the topic covers both).",
        "- Reddit weights use ~36h score snapshots; very recent posts are under-weighted.",
        "",
    ]
    FEATURES_DICT_PATH.write_text("\n".join(lines))
    return FEATURES_DICT_PATH


def main() -> None:
    ensure_data_dirs()
    cfg = load_features_config()
    docs = pd.read_parquet(DOCUMENTS_SCORED_PARQUET)
    print(f"Loaded {len(docs):,} scored documents")
    prep = prepare(docs, cfg)

    daily = build_daily(prep, cfg)
    daily.to_parquet(FEATURES_DAILY_PARQUET, index=False)
    print(f"Wrote {FEATURES_DAILY_PARQUET} ({len(daily):,} days × {daily.shape[1]} cols)")

    intraday = build_intraday(prep, cfg)
    intraday.to_parquet(FEATURES_INTRADAY_PARQUET, index=False)
    print(f"Wrote {FEATURES_INTRADAY_PARQUET} ({len(intraday):,} buckets × {intraday.shape[1]} cols)")

    print(f"Wrote {write_dictionary(daily, intraday, cfg)}")


if __name__ == "__main__":
    main()
