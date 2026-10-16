"""Financial news ingestion (RSS, Fed archives, GDELT, dedupe)."""

__all__ = ["collect_all", "save_news_raw", "dedupe_articles"]


def __getattr__(name: str):
    if name in {"collect_all", "save_news_raw"}:
        from src.ingestion.news import pipeline

        return getattr(pipeline, name)
    if name == "dedupe_articles":
        from src.ingestion.news.dedupe import dedupe_articles

        return dedupe_articles
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
