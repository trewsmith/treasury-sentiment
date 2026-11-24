# Sentiment Feature Dictionary

- **features_daily.parquet:** 5,226 trading days (2006-01-03 → 2026-11-20), 62 columns
- **features_intraday.parquet:** 249,132 buckets (5min, 30min, 60min), 55 columns
- Built by `src/features/pipeline.py` from `documents_scored.parquet`; config `configs/features.yaml`.

## Keys and timing

- **Daily `date`** = `yield_date`: the first DGS10 observation a document can affect (same ET day if before 15:30 ET, else next trading day). Join to `market_daily.csv` on `date`. Days with no documents have zero counts and null means.
- **Intraday `bucket_start_utc`** = bucket start (UTC); `bucket_freq` is `5min` or `30min`. Date-only news timestamps are excluded; intraday starts 2025-01-01.

## Columns (`<src>` = `news` or `reddit`)

| Column | Description |
|---|---|
| `n_<src>` | Documents in the period |
| `n_<src>_relevant` | Of those, `is_relevant` (news, macro topic, or yield cue) |
| `<src>_sent_n` | Docs with a finbert score (relevant docs only) |
| `<src>_sent_mean` | Mean finbert `sentiment_score` (p_pos − p_neg) |
| `<src>_sent_wmean` | Weighted mean finbert score: news by source quality, Reddit by 1 + log1p(score) |
| `<src>_vader_mean` | Mean VADER score over all docs (baseline) |
| `<src>_ydir_mean` / `_ydir_wmean` | Mean / weighted `yield_direction_signal` over relevant docs (+ = yields up) |
| `<src>_neg_spike` | Docs with finbert score ≤ -0.5 |
| `<src>_<topic>_sent_mean` | Mean tone of docs tagged with the topic |
| `<src>_<topic>_ydir_mean` | Mean yield-direction signal of docs tagged with the topic |
| `reddit_exwsb_*_mean` | Unweighted Reddit means excluding r/wallstreetbets |
| `n_press`, `press_*_mean` | News excluding Federal Reserve documents, unweighted |
| `n_topic_<topic>` | Docs (both sources) tagged with the topic |
| `*_z30` (daily) | Surprise: (x − trailing 30-day mean) / trailing std, prior days only |
| `shock_score` (intraday) | Doc-volume z-score vs the prior 24h of buckets |
| `ydir_pressure` (intraday) | Σ weight × yield_direction_signal in the bucket (signed) |

## Caveats

- finbert covers relevant documents only; `*_sent_*` features are null on days with no scored docs.
- `growth` topic features double as recession sentiment (the topic covers both).
- Reddit weights use ~36h score snapshots; very recent posts are under-weighted.
