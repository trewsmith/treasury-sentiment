# Treasury Sentiment

This research project examines the incorporation of textual financial information into U.S. Treasury yields, focusing on the timing, semantic content, and market conditions associated with yield movements. The study integrates financial natural language processing, time-series methods, and event-study analysis to evaluate information from professional financial news and social media.

**Principal Investigator:** Trew Smith
**Advisor:** Professor Lucas Cordova, Willamette University
**Research Group:** Cordova AI Lab


## Data pipelines

Run from the project root with the virtualenv active (`pip install -r requirements.txt`).

| Step | Command | Output (`data/processed/`) |
|------|---------|----------------------------|
| Market data (FRED) | `PYTHONPATH=. python src/ingestion/fred_client.py` | `market_daily.csv` |
| Macro event calendar | `PYTHONPATH=. python src/ingestion/events.py` | `events_calendar.parquet` |
| Intraday 10y + controls | `PYTHONPATH=. python src/ingestion/intraday.py` | `market_intraday.parquet` |
| News | `PYTHONPATH=. python src/ingestion/news/pipeline.py` | `news_raw.parquet` |
| Reddit posts | `PYTHONPATH=. python src/ingestion/reddit/pipeline.py` | `reddit_posts_raw.parquet` |
| Clean + align | `PYTHONPATH=. python src/cleaning/pipeline.py` | `documents_clean.parquet`, `data_quality_report.md` |
| Transformer sentiment | `PYTHONPATH=. .venv-ml/bin/python src/nlp/transformer_scoring.py --model finbert` (then `--model distilbert`) | cache in `data/interim/sentiment/` |
| Score documents | `PYTHONPATH=. python src/nlp/pipeline.py` | `documents_scored.parquet` (+ `docs/label_taxonomy.md`, `reports/`) |
| Sentiment factors | `PYTHONPATH=. python src/features/pipeline.py` | `features_daily.parquet`, `features_intraday.parquet`, `features_dictionary.md` |

| Daily regression | `PYTHONPATH=. python src/modeling/daily_regression.py` | `reports/tables/daily_regression.csv` |
| Intraday regression (5/30/60 min) | `PYTHONPATH=. python src/modeling/intraday_regression.py` | `reports/tables/intraday_regression.csv` |
| Event study (macro releases) | `PYTHONPATH=. python src/modeling/event_study.py` | `reports/tables/event_study.csv` |
| Classifier eval vs hand labels | `PYTHONPATH=. python src/evaluation/yield_direction_eval.py` | `reports/tables/yield_direction_eval.csv` |

Each output has a Markdown data dictionary next to it. Configs live in `configs/`
(`fred.yaml`, `news.yaml`, `reddit.yaml`, `cleaning.yaml`).

- **Reddit** uses the Arctic Shift archive (no credentials needed). Pulls are cached per
  subreddit-month in `data/raw/reddit/arctic_shift/`, so re-runs only fetch the current month.
  `--with-praw` adds the newest posts through the official API when `REDDIT_*` keys are set in `.env`.
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
  Labels are 850 **silver** (LLM-assigned) + 220 **hand** (`labeler == trew`, batches 1–2; sheets use
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
