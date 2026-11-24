"""Project path helpers."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIGS_DIR = PROJECT_ROOT / "configs"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

FRED_RAW_DIR = RAW_DIR / "fred"
NEWS_RAW_DIR = RAW_DIR / "news"
NEWS_INTERIM_DIR = INTERIM_DIR / "news"
REDDIT_RAW_DIR = RAW_DIR / "reddit"
MARKET_DAILY_PATH = PROCESSED_DIR / "market_daily.csv"
SP500_HISTORY_PATH = PROCESSED_DIR / "sp500_history.csv"
MARKET_DICT_PATH = PROCESSED_DIR / "market_daily_dictionary.md"
NEWS_RAW_PARQUET = PROCESSED_DIR / "news_raw.parquet"
NEWS_DICT_PATH = PROCESSED_DIR / "news_raw_dictionary.md"
REDDIT_POSTS_RAW_PARQUET = PROCESSED_DIR / "reddit_posts_raw.parquet"
REDDIT_DICT_PATH = PROCESSED_DIR / "reddit_posts_raw_dictionary.md"
DOCUMENTS_CLEAN_PARQUET = PROCESSED_DIR / "documents_clean.parquet"
DATA_QUALITY_REPORT_PATH = PROCESSED_DIR / "data_quality_report.md"
DOCUMENTS_SCORED_PARQUET = PROCESSED_DIR / "documents_scored.parquet"
FEATURES_DAILY_PARQUET = PROCESSED_DIR / "features_daily.parquet"
FEATURES_INTRADAY_PARQUET = PROCESSED_DIR / "features_intraday.parquet"
FEATURES_DICT_PATH = PROCESSED_DIR / "features_dictionary.md"

EVENTS_CALENDAR_PARQUET = PROCESSED_DIR / "events_calendar.parquet"
EVENTS_DICT_PATH = PROCESSED_DIR / "events_calendar_dictionary.md"
INTRADAY_RAW_DIR = RAW_DIR / "intraday"
MARKET_INTRADAY_PARQUET = PROCESSED_DIR / "market_intraday.parquet"
MARKET_HOURLY_PARQUET = PROCESSED_DIR / "market_hourly.parquet"
MARKET_INTRADAY_DICT_PATH = PROCESSED_DIR / "market_intraday_dictionary.md"

SENTIMENT_CACHE_DIR = INTERIM_DIR / "sentiment"
MODELS_DIR = INTERIM_DIR / "models"
LABELS_DIR = DATA_DIR / "labels"

REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
DOCS_DIR = PROJECT_ROOT / "docs"


def ensure_data_dirs() -> None:
    """Create standard data directories if missing."""
    for path in (
        RAW_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        FRED_RAW_DIR,
        NEWS_RAW_DIR,
        NEWS_INTERIM_DIR,
        REDDIT_RAW_DIR,
        INTRADAY_RAW_DIR,
        SENTIMENT_CACHE_DIR,
        MODELS_DIR,
        LABELS_DIR,
        TABLES_DIR,
        FIGURES_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
