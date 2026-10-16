"""
Orchestrate news ingestion → dedupe → news_raw.parquet.

Usage:
  PYTHONPATH=. python src/ingestion/news/pipeline.py
  PYTHONPATH=. python src/ingestion/news/pipeline.py --skip-enrich
  PYTHONPATH=. python src/ingestion/news/pipeline.py --with-gdelt
  PYTHONPATH=. python src/ingestion/news/pipeline.py --merge-existing --skip-fed
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yaml

from src.ingestion.news.dedupe import dedupe_articles
from src.ingestion.news.enrich import enrich_bodies
from src.ingestion.news.fed import fetch_fed_json_sources
from src.ingestion.news.gdelt import fetch_gdelt_history
from src.ingestion.news.gdelt_bulk import fetch_gdelt_timespan_bulk
from src.ingestion.news.google_news import fetch_google_news_queries
from src.ingestion.news.http_util import make_session
from src.ingestion.news.listings import fetch_listings
from src.ingestion.news.rss import fetch_rss_feeds
from src.ingestion.news.schema import ARTICLE_COLUMNS, empty_articles_frame
from src.utils.paths import (
    CONFIGS_DIR,
    NEWS_DICT_PATH,
    NEWS_INTERIM_DIR,
    NEWS_RAW_DIR,
    NEWS_RAW_PARQUET,
    ensure_data_dirs,
)


def load_news_config(path: Path | None = None) -> dict:
    cfg_path = path or (CONFIGS_DIR / "news.yaml")
    with open(cfg_path) as f:
        return yaml.safe_load(f)


def _save_interim(df: pd.DataFrame, name: str) -> Path:
    ensure_data_dirs()
    path = NEWS_INTERIM_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def collect_rss_all(cfg: dict, session) -> pd.DataFrame:
    frames = []
    for source, feeds in (cfg.get("rss_feeds") or {}).items():
        frames.append(fetch_rss_feeds(feeds, source=source, session=session))
    return pd.concat(frames, ignore_index=True) if frames else empty_articles_frame()


def collect_all(
    cfg: dict,
    *,
    skip_gdelt: bool = False,
    skip_enrich: bool = False,
    skip_fed: bool = False,
    skip_rss: bool = False,
    skip_listings: bool = False,
    gdelt_mode: str = "timespan",
    existing: pd.DataFrame | None = None,
) -> pd.DataFrame:
    ensure_data_dirs()
    session = make_session()
    parts: list[pd.DataFrame] = []
    if existing is not None and not existing.empty:
        parts.append(existing)

    if not skip_rss:
        print("=== RSS feeds ===")
        rss_df = collect_rss_all(cfg, session)
        _save_interim(rss_df, "rss")
        parts.append(rss_df)
        print(f"RSS total: {len(rss_df)}")

        print("=== Google News ===")
        gnews_df = fetch_google_news_queries(
            cfg.get("google_news_queries") or [],
            when="1y",
            session=session,
        )
        _save_interim(gnews_df, "google_news")
        parts.append(gnews_df)
        print(f"Google News total: {len(gnews_df)}")

    if not skip_listings:
        print("=== Listing pages (CNBC / Yahoo) ===")
        listings_df = fetch_listings(session=session)
        _save_interim(listings_df, "listings")
        parts.append(listings_df)
        print(f"Listings total: {len(listings_df)}")

    if not skip_fed:
        print("=== Federal Reserve JSON archives ===")
        fed_df = fetch_fed_json_sources(cfg.get("fed_json") or [], session=session)
        _save_interim(fed_df, "fed")
        parts.append(fed_df)
        print(f"Fed total: {len(fed_df)}")

    if not skip_gdelt:
        print(f"=== GDELT ({gdelt_mode}) ===")
        sleep_s = float(cfg.get("gdelt_sleep_seconds") or 6.5)
        if gdelt_mode == "windows":
            years = float(cfg.get("lookback_years") or 0.25)
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=int(365 * years))
            gdelt_cfg = cfg.get("gdelt") or {}
            import time as time_module

            time_module.sleep(10)
            gdelt_df = fetch_gdelt_history(
                gdelt_cfg.get("queries") or [],
                start=start,
                end=end,
                window_days=int(gdelt_cfg.get("window_days") or 2),
                maxrecords=int(gdelt_cfg.get("maxrecords") or 250),
                sleep_seconds=sleep_s,
                session=session,
            )
        else:
            gdelt_df = fetch_gdelt_timespan_bulk(
                sleep_seconds=sleep_s,
                session=session,
            )
        _save_interim(gdelt_df, "gdelt")
        parts.append(gdelt_df)
        print(f"GDELT total: {len(gdelt_df)}")

    combined = (
        pd.concat([p for p in parts if p is not None and not p.empty], ignore_index=True)
        if parts
        else empty_articles_frame()
    )
    _save_interim(combined, "combined_raw")
    print(f"Combined raw: {len(combined)}")

    print("=== Dedup ===")
    deduped = dedupe_articles(combined)
    _save_interim(deduped, "deduped")

    if not skip_enrich:
        print("=== Body enrichment ===")
        body_cfg = cfg.get("body_fetch") or {}
        if body_cfg.get("enabled", True):
            deduped = enrich_bodies(
                deduped,
                max_articles=int(body_cfg.get("max_articles") or 2500),
                sleep_seconds=float(body_cfg.get("sleep_seconds") or 0.4),
                source_priority=body_cfg.get("sources_priority"),
            )
            _save_interim(deduped, "enriched")

    return deduped


def write_data_dictionary(df: pd.DataFrame, path: Path = NEWS_DICT_PATH) -> Path:
    by_source = df["source"].value_counts(dropna=False).to_dict() if len(df) else {}
    by_method = (
        df["ingest_method"].value_counts(dropna=False).to_dict() if len(df) else {}
    )
    with_body = int((df["body"].fillna("").astype(str).str.len() >= 40).sum()) if len(df) else 0
    date_min = df["published_at_utc"].min() if len(df) else None
    date_max = df["published_at_utc"].max() if len(df) else None

    lines = [
        "# news_raw.parquet — Data Dictionary",
        "",
        f"- **File:** `data/processed/news_raw.parquet`",
        f"- **Rows:** {len(df):,}",
        f"- **With body (≥40 chars):** {with_body:,}",
        f"- **Published range:** {date_min} → {date_max}",
        "",
        "## Columns",
        "",
        "| Column | Description |",
        "|--------|-------------|",
        "| article_id | SHA256-based id from normalized URL (fallback: headline) |",
        "| source | Publisher label (cnbc, marketwatch, federal_reserve, …) |",
        "| headline | Article title |",
        "| body | Full text when available (RSS summary or fetched HTML) |",
        "| published_at_utc | Publication / seen time in UTC |",
        "| url | Canonical article URL |",
        "| section | Feed section or Fed press type |",
        "| tag | Secondary label (RSS tags, speaker, gdelt, …) |",
        "| ingest_method | rss / google_news_rss / fed_json / listing / gdelt |",
        "| collected_at_utc | When this pipeline collected the row |",
        "",
        "## Counts by source",
        "",
    ]
    for src, n in sorted(by_source.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"- `{src}`: {n:,}")
    lines.extend(["", "## Counts by ingest_method", ""])
    for method, n in sorted(by_method.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"- `{method}`: {n:,}")
    lines.extend(
        [
            "",
            "## Source strategy",
            "",
            "- **MarketWatch / CNBC / Investing.com / Fed / Seeking Alpha / Guardian:** public RSS.",
            "- **Federal Reserve archives:** official JSON (press, speeches, testimony) — multi-year.",
            "- **Google News RSS:** treasury/Fed/inflation topic queries (≈1y).",
            "- **CNBC / Yahoo Finance listings:** public section/topic pages.",
            "- **Yahoo Finance / Reuters RSS:** currently unreliable; use listings/Google News/GDELT.",
            "- **GDELT DOC 2.1:** optional historical headlines (strict rate limits).",
            "- **Bloomberg scraping:** intentionally avoided.",
            "- **Dedup:** exact `article_id` (normalized URL), then headline+day near-dupes.",
            "",
        ]
    )
    path.write_text("\n".join(lines))
    return path


def save_news_raw(df: pd.DataFrame) -> Path:
    ensure_data_dirs()
    # Also keep a raw snapshot under data/raw/news
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_snap = NEWS_RAW_DIR / f"news_raw_{stamp}.parquet"
    ordered = df[[c for c in ARTICLE_COLUMNS if c in df.columns]]
    ordered.to_parquet(NEWS_RAW_PARQUET, index=False)
    ordered.to_parquet(raw_snap, index=False)
    write_data_dictionary(ordered)
    return NEWS_RAW_PARQUET


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest financial news → news_raw.parquet")
    parser.add_argument(
        "--with-gdelt",
        action="store_true",
        help="Include GDELT (optional; often rate-limited)",
    )
    parser.add_argument("--skip-enrich", action="store_true", help="Skip HTML body fetch")
    parser.add_argument("--skip-fed", action="store_true", help="Skip Fed JSON archives")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS + Google News")
    parser.add_argument("--skip-listings", action="store_true", help="Skip CNBC/Yahoo listings")
    parser.add_argument(
        "--gdelt-mode",
        choices=["timespan", "windows"],
        default="timespan",
        help="GDELT collection strategy when --with-gdelt is set",
    )
    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="Merge with existing data/processed/news_raw.parquet",
    )
    parser.add_argument(
        "--gdelt-years",
        type=float,
        default=None,
        help="Override lookback_years for GDELT sweep",
    )
    args = parser.parse_args()

    cfg = load_news_config()
    if args.gdelt_years is not None:
        cfg["lookback_years"] = args.gdelt_years

    existing = None
    if args.merge_existing and NEWS_RAW_PARQUET.exists():
        existing = pd.read_parquet(NEWS_RAW_PARQUET)
        print(f"Loaded existing {len(existing):,} articles from {NEWS_RAW_PARQUET}")

    df = collect_all(
        cfg,
        skip_gdelt=not args.with_gdelt,
        skip_enrich=args.skip_enrich,
        skip_fed=args.skip_fed,
        skip_rss=args.skip_rss,
        skip_listings=args.skip_listings,
        gdelt_mode=args.gdelt_mode,
        existing=existing,
    )
    path = save_news_raw(df)
    print(f"Wrote {path} ({len(df):,} articles)")
    print(f"Wrote {NEWS_DICT_PATH}")
    print(df["source"].value_counts().head(15))


if __name__ == "__main__":
    main()
