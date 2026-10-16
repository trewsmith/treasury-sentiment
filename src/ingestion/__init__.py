"""Data ingestion (FRED and other sources)."""

__all__ = ["fetch_series", "save_raw_series", "merge_market_series"]


def __getattr__(name: str):
    if name in __all__:
        from src.ingestion import fred_client

        return getattr(fred_client, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
