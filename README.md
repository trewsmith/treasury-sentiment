# Treasury Sentiment

This research project examines the incorporation of textual financial information into U.S. Treasury yields, focusing on the timing, semantic content, and market conditions associated with yield movements. The study integrates financial natural language processing, time-series methods, and event-study analysis to evaluate information from professional financial news and social media.

**Principal Investigator:** Trew Smith
**Advisor:** Professor Lucas Cordova, Willamette University
**Research Group:** Cordova AI Lab


## Scope and primary result

**Lead finding (exploratory).** Same-day Reddit tone (FinBERT, unweighted) and the daily change in the **2-year**
Treasury yield, 2025+: +0.78 bp per 1 SD, Holm p = 0.003 within the `reddit_robustness.csv` test family (n = 472,
no 2-year control). Unweighted avoids weights built from post scores observed ~36h later. Score-weighted: +0.90
(Holm p < 0.001); excluding r/wallstreetbets: +0.81 (Holm p = 0.003).
This outcome was chosen after seeing the results, so it is exploratory, not pre-specified. It is a same-day
association: it does not show that Reddit causes or predicts yields, and posts may be reacting to yield moves.

**Checks of the lead result** (`lead_result_checks.csv`, post hoc, its own Holm family). Same-day +0.76 to +0.80 with no
controls, lagged 2-year change, Reddit volume or press controls (Holm p <= 0.010); 2025-11-24+ +1.03 (Holm p = 0.005);
before that +0.46 (p = 0.110), so it is not established in the earlier half. No lead: next-day -0.20 (p = 0.38). Splitting
posts by time of day, overnight (before 08:00 ET) +0.52 and session +0.56 are each nominal only (Holm p = 0.73, 0.12), so
the data cannot say whether posts move before or after the market.

**Secondary: 10-year yield.** Unweighted +0.53 bp, Holm p = 0.41; score-weighted +0.67 bp, Holm p = 0.080 (+0.62, Holm p = 0.042
in `daily_regression.csv`), and about zero once the 2-year change is controlled for. Not significant after Holm
correction in the press-covered window (2025-11-24+). No text measure significantly led the 10-year after Holm
correction in the lead/lag or hourly tests.

**Information categories.** Limited to the five tested: **inflation, Fed, growth, labor, fiscal**
(`regime_category.csv`). One survives Holm correction: Reddit **fiscal** direction, 2025+, with the 2-year control,
-0.38 bp (Holm p = 0.003); without that control, -0.52 (p = 0.019, Holm p = 0.19). The sign is opposite to the
label's meaning (up-pressure text, lower yields), so treat it as unexplained. Hawkish/dovish and risk-on/risk-off are out of scope.

**Limitations.** Press coverage is nearly empty in 2025 Q2-Q3; many press items have date-only times; 5- and
30-minute tests cover about three months and are exploratory; the yield-direction classifier is weak on "down"
(F1 0.37 on hand labels).

## Data pipelines

Run from the project root with the virtualenv active (`pip install -r requirements.txt`).

| Step | Command | Output (`data/processed/`) |
|------|---------|----------------------------|
| Market data (FRED) | `PYTHONPATH=. python src/ingestion/fred_client.py` | `market_daily.csv` |
| S&P 500 history (FRED has ~10y) | `PYTHONPATH=. python src/ingestion/sp500_history.py` | `sp500_history.csv` |
| Macro event calendar | `PYTHONPATH=. python src/ingestion/events.py` | `events_calendar.parquet` |
| Intraday 10y + controls | `PYTHONPATH=. python src/ingestion/intraday.py` | `market_intraday.parquet`, `market_hourly.parquet` (~730 days) |
| News | `PYTHONPATH=. python src/ingestion/news/pipeline.py` | `news_raw.parquet` |
| GDELT headline backfill (resumable, slow) | `PYTHONPATH=. python src/ingestion/news/gdelt_backfill.py --days 7 --sleep 60 --queries rates` | cache in `data/raw/news/gdelt_windows/` |
| Merge all collected news | `PYTHONPATH=. python src/ingestion/news/merge_history.py` | `news_raw.parquet`, `data/labels/label_texts.parquet` |
| Reddit posts | `PYTHONPATH=. python src/ingestion/reddit/pipeline.py` | `reddit_posts_raw.parquet` |
| Clean + align | `PYTHONPATH=. python src/cleaning/pipeline.py` | `documents_clean.parquet`, `data_quality_report.md` |
| Transformer sentiment | `PYTHONPATH=. .venv-ml/bin/python src/nlp/transformer_scoring.py --model finbert` (then `--model distilbert`) | cache in `data/interim/sentiment/` |
| Score documents | `PYTHONPATH=. python src/nlp/pipeline.py` | `documents_scored.parquet` (+ `docs/label_taxonomy.md`, `reports/`) |
| Sentiment factors | `PYTHONPATH=. python src/features/pipeline.py` | `features_daily.parquet`, `features_intraday.parquet`, `features_dictionary.md` |

| Daily regression | `PYTHONPATH=. python src/modeling/daily_regression.py` | `reports/tables/daily_regression.csv` |
| Regime + info-category (daily) | `PYTHONPATH=. python src/modeling/regime_category.py` | `reports/tables/regime_category.csv` |
| Intraday regression (5/30/60 min) | `PYTHONPATH=. python src/modeling/intraday_regression.py` | `reports/tables/intraday_regression.csv` |
| Hourly regression (2025+) | `PYTHONPATH=. python src/modeling/hourly_regression.py` | `reports/tables/hourly_regression.csv` |
| Reddit robustness (daily) | `PYTHONPATH=. python src/modeling/reddit_robustness.py` | `reports/tables/reddit_robustness.csv` |
| News robustness + news vs. Reddit windows | `PYTHONPATH=. python src/modeling/news_robustness.py` | `reports/tables/news_robustness.csv`, `news_vs_reddit_windows.csv` |
| Lead/lag timing (daily) | `PYTHONPATH=. python src/modeling/lead_lag.py` | `reports/tables/lead_lag.csv` |
| Lead-result checks (2-year) | `PYTHONPATH=. python src/modeling/lead_result_checks.py` | `reports/tables/lead_result_checks.csv` |
| Descriptive tables | `PYTHONPATH=. python src/modeling/descriptives.py` | `reports/tables/desc_*.csv` |
| Event study (macro releases) | `PYTHONPATH=. python src/modeling/event_study.py` | `reports/tables/event_study.csv` |
| Classifier eval vs hand labels | `PYTHONPATH=. python src/evaluation/yield_direction_eval.py` | `reports/tables/yield_direction_eval.csv` |
| Everything after data collection, inputs hashed | `bash scripts/frozen_rerun.sh` | `reports/tables/`, `reports/paper/` |
| Paper tables + figures (run last) | `PYTHONPATH=. python src/reporting_paper.py` | `reports/paper/` |

Each output has a Markdown data dictionary next to it. Configs live in `configs/`
(`fred`, `news`, `reddit`, `cleaning`, `events`, `intraday`, `features`, `taxonomy` `.yaml`).

- **Reddit** uses the Arctic Shift archive (no credentials needed). Pulls are cached per
  subreddit-month in `data/raw/reddit/arctic_shift/`, so re-runs only fetch the current month.
  `--with-praw` adds the newest posts through the official API when `REDDIT_*` keys are set in `.env`.
- **News refreshes merge by default.** Feeds only serve recent items; `--no-merge-existing` drops older articles.
- **Placeholder times:** Google News midnight-Pacific stamps and date-only CNBC listings are moved to 23:59:59 ET
  (date-only, next `yield_date`) because their real publication time is unknown.
- **Cleaning** merges news and Reddit into one canonical schema (`doc_id, source_type,
  source_name, timestamp_utc, headline, body, text, meta`) plus time-alignment columns. Use
  `yield_date` to join documents to `market_daily.csv` `date`.

```python
import pandas as pd
from src.cleaning.documents import expand_meta

docs = pd.read_parquet("data/processed/documents_clean.parquet")
market = pd.read_csv("data/processed/market_daily.csv", parse_dates=["date"])
daily = docs.merge(market, left_on="yield_date", right_on="date", how="left")
reddit = expand_meta(docs[docs.source_type == "reddit"])  # meta_score, meta_subreddit, …
```

### Transformer models (separate environment)

PyTorch has no builds for Python 3.14 or for Intel Macs after torch 2.2, so DistilBERT
and FinBERT run in a second virtualenv on Python 3.12:

```bash
brew install python@3.12
/usr/local/opt/python@3.12/bin/python3.12 -m venv .venv-ml
.venv-ml/bin/pip install -r requirements-ml.txt
```

Only relevant documents are scored (all news, plus Reddit posts with a macro topic or a
yield-direction cue). Scores are cached per text hash, so re-runs only score new text.

### Sentiment layers

- **Layer 1, tone:** VADER, DistilBERT (binary), FinBERT → `<model>_p_positive / _p_neutral /
  _p_negative / _sentiment_score / _confidence / _entropy`. Compare them in
  `notebooks/01_sentiment_benchmark.ipynb`.
- **Layer 2, yield direction:** regex rules (`configs/taxonomy.yaml`) plus a classifier trained on
  `data/labels/yield_direction_labels.csv` → `yield_direction_signal` (+ = pushes 10y yields up).
  Labels are 850 **silver** (LLM-assigned) + 340 **hand** (`labeler == trew`, batches 1–3; sheets use
  short codes p=up, n=down, u=neutral, which `merge` accepts). Batch 2 is an enriched sample
  (down / uncertain-up oversampled), so use it for per-class metrics, not base rates.
  Add or correct labels in that file and re-run `src/nlp/pipeline.py`. To get a fresh stratified sheet:
  `PYTHONPATH=. python src/nlp/pipeline.py --export-label-sample 1000`; for a blinded hand batch use
  `src/labeling/hand_labels.py make|make-enriched|merge` (raw returned sheets go in `data/labels/raw/`).
  Evaluate against the hand labels (train on silver, test on gold):
  `PYTHONPATH=. python src/evaluation/yield_direction_eval.py` → `reports/tables/yield_direction_eval.csv`.
- **Topics:** 8 macro topic tags (`topic_*`) with monthly tables in `reports/tables/`.

**Intraday caveat:** Yahoo serves only ~60 days of 5-minute bars, so `market_intraday.parquet`
accumulates only if `src/ingestion/intraday.py` is run regularly (or vendor files are added to
`data/raw/intraday/vendor/`). The intraday regression is underpowered until then.

Large outputs (`reddit_posts_raw`, `documents_clean`, `documents_scored`, `features_intraday`)
exceed GitHub's file limit and are gitignored; rebuild them with the commands above.

Tests: `PYTHONPATH=. python -m pytest tests`
