# news_raw.parquet — Data Dictionary

- **File:** `data/processed/news_raw.parquet`
- **Rows:** 8,459
- **With body (≥40 chars):** 3,785
- **Published range:** 2006-01-03 05:00:00+00:00 → 2026-10-16 20:35:42+00:00

## Columns

| Column | Description |
|--------|-------------|
| article_id | SHA256-based id from normalized URL (fallback: headline) |
| source | Publisher label (cnbc, marketwatch, federal_reserve, …) |
| headline | Article title |
| body | Full text when available (RSS summary or fetched HTML) |
| published_at_utc | Publication / seen time in UTC |
| url | Canonical article URL |
| section | Feed section or Fed press type |
| tag | Secondary label (RSS tags, speaker, gdelt, …) |
| ingest_method | rss / google_news_rss / fed_json / listing / gdelt |
| collected_at_utc | When this pipeline collected the row |

## Counts by source

- `federal_reserve`: 6,245
- `google_news`: 1,786
- `cnbc`: 150
- `yahoo_finance`: 111
- `marketwatch`: 60
- `seeking_alpha`: 37
- `investing`: 36
- `guardian`: 34

## Counts by ingest_method

- `fed_json`: 6,200
- `google_news_rss`: 1,786
- `rss`: 326
- `listing`: 147

## Source strategy

- **MarketWatch / CNBC / Investing.com / Fed / Seeking Alpha / Guardian:** public RSS.
- **Federal Reserve archives:** official JSON (press, speeches, testimony) — multi-year.
- **Google News RSS:** treasury/Fed/inflation topic queries (≈1y).
- **CNBC / Yahoo Finance listings:** public section/topic pages.
- **Yahoo Finance / Reuters RSS:** currently unreliable; use listings/Google News/GDELT.
- **GDELT DOC 2.1:** optional historical headlines (strict rate limits).
- **Bloomberg scraping:** intentionally avoided.
- **Dedup:** exact `article_id` (normalized URL), then headline+day near-dupes.
