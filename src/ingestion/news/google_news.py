"""Google News RSS search queries (student-friendly, no API key)."""

from __future__ import annotations

from urllib.parse import quote_plus

import pandas as pd
import requests

from src.ingestion.news.http_util import make_session
from src.ingestion.news.rss import fetch_rss_feed
from src.ingestion.news.schema import records_to_frame


def _google_news_rss_url(query: str, when: str = "1y") -> str:
    q = f"{query} when:{when}"
    return (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"
    )


def fetch_google_news_queries(
    queries: list[dict],
    *,
    when: str = "1y",
    session: requests.Session | None = None,
) -> pd.DataFrame:
    sess = session or make_session()
    records: list[dict] = []
    for item in queries:
        url = _google_news_rss_url(item["query"], when=when)
        batch = fetch_rss_feed(
            url,
            source="google_news",
            section=item.get("section"),
            session=sess,
        )
        # Mark ingest method more specifically
        for rec in batch:
            rec["ingest_method"] = "google_news_rss"
            rec["source"] = "google_news"
        print(f"[google_news] {item.get('section')} -> {len(batch)}")
        records.extend(batch)
    return records_to_frame(records)
