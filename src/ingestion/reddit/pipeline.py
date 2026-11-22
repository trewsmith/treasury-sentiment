"""
Orchestrate Reddit submission ingestion → reddit_posts_raw.parquet.

Posts only (no comments). Arctic Shift provides history; PRAW optionally tops
up the newest posts when credentials are configured.

Usage:
  PYTHONPATH=. python src/ingestion/reddit/pipeline.py
  PYTHONPATH=. python src/ingestion/reddit/pipeline.py --start 2025-06-01 --subreddits bonds Economics
  PYTHONPATH=. python src/ingestion/reddit/pipeline.py --with-praw
  PYTHONPATH=. python src/ingestion/reddit/pipeline.py --refresh   # ignore month cache
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from src.ingestion.news.http_util import make_session
from src.ingestion.reddit.arctic_shift import DEFAULT_BASE_URL, fetch_subreddit_history
from src.ingestion.reddit.praw_client import fetch_recent_posts
from src.ingestion.reddit.schema import REDDIT_POST_COLUMNS, empty_posts_frame
from src.utils.paths import (
    CONFIGS_DIR,
    REDDIT_DICT_PATH,
    REDDIT_POSTS_RAW_PARQUET,
    ensure_data_dirs,
)

# Lower rank wins when the same post_id comes from several backends: archive
# rows are kept so score snapshots stay comparable across the sample.
INGEST_PRIORITY = {"arctic_shift": 0, "praw": 1}


def load_reddit_config(path: Path | None = None) -> dict:
    cfg_path = path or (CONFIGS_DIR / "reddit.yaml")
    with open(cfg_path) as f:
        return yaml.safe_load(f)


def _parse_utc(value: str | None, default: datetime) -> datetime:
    if not value:
        return default
    return pd.Timestamp(value, tz="UTC").to_pydatetime()


def dedupe_posts(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate post_ids (preferring archive rows, then latest collection)."""
    if df.empty:
        return df.copy()
    out = df.assign(_rank=df["ingest_method"].map(INGEST_PRIORITY).fillna(9))
    out = out.sort_values(["_rank", "collected_at_utc"], ascending=[True, False])
    before = len(out)
    out = out.drop_duplicates(subset=["post_id"], keep="first")
    print(f"[dedupe] {before:,} → {len(out):,} (post_id)")
    out = out.drop(columns="_rank").sort_values(["created_utc", "post_id"])
    return out[REDDIT_POST_COLUMNS].reset_index(drop=True)


def collect_all(
    cfg: dict,
    *,
    start: datetime,
    end: datetime,
    subreddits: list[str],
    with_praw: bool = False,
    skip_archive: bool = False,
    refresh: bool = False,
    existing: pd.DataFrame | None = None,
) -> pd.DataFrame:
    ensure_data_dirs()
    parts: list[pd.DataFrame] = []
    if existing is not None and not existing.empty:
        parts.append(existing)

    if not skip_archive:
        print(f"=== Arctic Shift ({start:%Y-%m-%d} → {end:%Y-%m-%d}) ===")
        as_cfg = cfg.get("arctic_shift") or {}
        session = make_session()
        for name in subreddits:
            df = fetch_subreddit_history(
                name,
                start,
                end,
                session=session,
                base_url=as_cfg.get("base_url") or DEFAULT_BASE_URL,
                page_size=int(as_cfg.get("page_size") or 100),
                sleep_seconds=float(as_cfg.get("sleep_seconds") or 0.5),
                cache_after_days=float(as_cfg.get("cache_after_days") or 3),
                refresh=refresh,
            )
            print(f"r/{name} total: {len(df):,}")
            parts.append(df)

    if with_praw:
        print("=== PRAW (newest posts) ===")
        praw_cfg = cfg.get("praw") or {}
        praw_df = fetch_recent_posts(
            subreddits,
            limit_per_subreddit=int(praw_cfg.get("limit_per_subreddit") or 1000),
            since=start,
        )
        if not praw_df.empty:
            praw_df = praw_df[praw_df["created_utc"] < pd.Timestamp(end)]
        parts.append(praw_df)

    parts = [p for p in parts if p is not None and not p.empty]
    combined = pd.concat(parts, ignore_index=True) if parts else empty_posts_frame()
    print(f"Combined raw: {len(combined):,}")
    return dedupe_posts(combined)


def write_data_dictionary(df: pd.DataFrame, path: Path = REDDIT_DICT_PATH) -> Path:
    n = len(df)
    by_sub = df["subreddit"].value_counts().to_dict() if n else {}
    by_method = df["ingest_method"].value_counts().to_dict() if n else {}
    removed = df["removed_by_category"].fillna("(not removed)").value_counts().to_dict() if n else {}
    with_text = (
        int((~df["selftext"].fillna("").isin(["", "[removed]", "[deleted]"])).sum()) if n else 0
    )
    date_min = df["created_utc"].min() if n else None
    date_max = df["created_utc"].max() if n else None

    lines = [
        "# reddit_posts_raw.parquet — Data Dictionary",
        "",
        "- **File:** `data/processed/reddit_posts_raw.parquet`",
        f"- **Rows:** {n:,} (submissions only; comments not collected)",
        f"- **With usable selftext:** {with_text:,} (rest are link/title-only, removed or deleted)",
        f"- **Created range:** {date_min} → {date_max}",
        "",
        "## Columns",
        "",
        "| Column | Description |",
        "|--------|-------------|",
        "| post_id | Reddit base36 submission id (no `t3_` prefix); unique |",
        "| subreddit | Subreddit name, lowercased |",
        "| title | Post title |",
        "| selftext | Post body for text posts; null for link posts. May be `[removed]` / `[deleted]` |",
        "| author | Username; `[deleted]` when the account was deleted (kept, not filtered) |",
        "| score | Net upvotes at `score_observed_at_utc` |",
        "| upvote_ratio | Share of upvotes at observation time |",
        "| num_comments | Comment count at observation time |",
        "| created_utc | Post creation time (UTC, second precision) |",
        "| permalink | Full https://www.reddit.com/… link to the post |",
        "| url | Outbound link for link posts (equals permalink-style URL for text posts) |",
        "| domain | Link domain (`self.<subreddit>` for text posts) |",
        "| is_self | True for text posts |",
        "| link_flair_text | Post flair (e.g. `Discussion`, `DD`, `Daily Discussion`) |",
        "| over_18 | NSFW flag |",
        "| stickied | Pinned by moderators (megathreads, rules posts) |",
        "| distinguished | `moderator` / `admin` when posted in an official capacity |",
        "| removed_by_category | Removal reason if removed (`moderator`, `automod_filtered`, `reddit`, `deleted`, …) |",
        "| crosspost_parent | Fullname of the original post if this is a crosspost |",
        "| ingest_method | `arctic_shift` (archive) or `praw` (official API) |",
        "| score_observed_at_utc | When score / num_comments / removal were captured |",
        "| collected_at_utc | When this pipeline collected the row |",
        "",
        "## Counts by subreddit",
        "",
    ]
    for name, k in sorted(by_sub.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"- `r/{name}`: {k:,}")
    lines.extend(["", "## Counts by ingest_method", ""])
    for method, k in sorted(by_method.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"- `{method}`: {k:,}")
    lines.extend(["", "## Counts by removed_by_category", ""])
    for cat, k in sorted(removed.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"- `{cat}`: {k:,}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- **Source:** Arctic Shift archive (Pushshift successor) for history, chunked by "
            "subreddit-month and cached in `data/raw/reddit/arctic_shift/`. Optional PRAW top-up "
            "for the newest posts (`--with-praw`).",
            "- **Scores are snapshots.** Archive rows carry the score from Arctic Shift's second "
            "retrieval, typically ~36h after posting (`score_observed_at_utc`); posts newer than "
            "that still show near-zero scores. PRAW rows are observed at collection time. Do not "
            "mix the two without accounting for this.",
            "- **Raw = unfiltered.** Removed, deleted, stickied and NSFW posts are kept here; "
            "filtering happens in `src/cleaning/pipeline.py` → `documents_clean.parquet`.",
            "- **Comments:** intentionally out of scope for the first pass.",
            "",
        ]
    )
    path.write_text("\n".join(lines))
    return path


def save_reddit_raw(df: pd.DataFrame) -> Path:
    ensure_data_dirs()
    df[REDDIT_POST_COLUMNS].to_parquet(REDDIT_POSTS_RAW_PARQUET, index=False)
    write_data_dictionary(df)
    return REDDIT_POSTS_RAW_PARQUET


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Reddit posts → reddit_posts_raw.parquet")
    parser.add_argument("--start", default=None, help="UTC start date (default: config start_date)")
    parser.add_argument("--end", default=None, help="UTC end date, exclusive (default: now)")
    parser.add_argument(
        "--subreddits", nargs="+", default=None, help="Override configured subreddits"
    )
    parser.add_argument(
        "--with-praw", action="store_true", help="Top up newest posts via PRAW (needs .env creds)"
    )
    parser.add_argument("--skip-archive", action="store_true", help="Skip Arctic Shift")
    parser.add_argument("--refresh", action="store_true", help="Re-pull cached archive months")
    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="Merge with existing data/processed/reddit_posts_raw.parquet",
    )
    args = parser.parse_args()

    cfg = load_reddit_config()
    now = datetime.now(timezone.utc)
    start = _parse_utc(args.start or cfg.get("start_date"), default=now)
    end = _parse_utc(args.end or cfg.get("end_date"), default=now)
    if start >= end:
        parser.error(f"start ({start}) must be before end ({end})")
    subreddits = args.subreddits or list((cfg.get("subreddits") or {}).keys())

    existing = None
    if args.merge_existing and REDDIT_POSTS_RAW_PARQUET.exists():
        existing = pd.read_parquet(REDDIT_POSTS_RAW_PARQUET)
        print(f"Loaded existing {len(existing):,} posts from {REDDIT_POSTS_RAW_PARQUET}")

    df = collect_all(
        cfg,
        start=start,
        end=end,
        subreddits=subreddits,
        with_praw=args.with_praw,
        skip_archive=args.skip_archive,
        refresh=args.refresh,
        existing=existing,
    )
    path = save_reddit_raw(df)
    print(f"Wrote {path} ({len(df):,} posts)")
    print(f"Wrote {REDDIT_DICT_PATH}")
    if len(df):
        print(df["subreddit"].value_counts())


if __name__ == "__main__":
    main()
