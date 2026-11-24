set -eo pipefail
cd /Users/trewsmith/Desktop/treasury-sentiment; export PYTHONPATH=.; P=.venv/bin/python
shasum -a 256 data/processed/news_raw.parquet data/processed/reddit_posts_raw.parquet data/processed/market_*.* data/processed/sp500_history.csv data/processed/events_calendar.parquet data/labels/yield_direction_labels.csv data/labels/label_texts.parquet > data/interim/frozen_inputs.txt
$P src/cleaning/pipeline.py
for m in finbert distilbert; do HF_HUB_OFFLINE=1 .venv-ml/bin/python src/nlp/transformer_scoring.py --model $m; done
$P src/nlp/pipeline.py; $P src/features/pipeline.py
for m in daily_regression regime_category intraday_regression hourly_regression event_study reddit_robustness news_robustness lead_lag lead_result_checks descriptives; do $P src/modeling/$m.py; done
$P src/evaluation/yield_direction_eval.py; $P src/reporting_paper.py; $P -m pytest tests -q | tail -1
shasum -a 256 -c data/interim/frozen_inputs.txt
(echo "# Frozen inputs (sha256) for reports/paper, run $(date '+%Y-%m-%d %H:%M %Z')"; cat data/interim/frozen_inputs.txt) > reports/paper/frozen_inputs.txt
for e in .venv .venv-ml; do echo "# $e: $($e/bin/python --version)"; $e/bin/python -m pip freeze; done > reports/paper/environment.txt
