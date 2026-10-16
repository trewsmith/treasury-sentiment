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
MARKET_DAILY_PATH = PROCESSED_DIR / "market_daily.csv"
MARKET_DICT_PATH = PROCESSED_DIR / "market_daily_dictionary.md"
NEWS_RAW_PARQUET = PROCESSED_DIR / "news_raw.parquet"
NEWS_DICT_PATH = PROCESSED_DIR / "news_raw_dictionary.md"


def ensure_data_dirs() -> None:
    """Create standard data directories if missing."""
    for path in (
        RAW_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        FRED_RAW_DIR,
        NEWS_RAW_DIR,
        NEWS_INTERIM_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
