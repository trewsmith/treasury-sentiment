"""
Faster GDELT collection via timespan queries (no day-window crawl).

Each query returns up to 250 articles for the timespan. Many overlapping
topic/domain queries still produce thousands of unique URLs after dedupe,
without hammering the API with hundreds of dated requests.
"""

from __future__ import annotations

import json
import time

import pandas as pd
import requests

from src.ingestion.news.gdelt import _map_source, _parse_seendate
from src.ingestion.news.http_util import make_session
from src.ingestion.news.schema import article_record, records_to_frame

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# Intentionally diverse to maximize unique URLs under the 250-cap
TIMESPAN_QUERIES: list[dict] = [
    {"name": "cnbc_treasury", "query": 'domain:cnbc.com (treasury OR FOMC OR yields OR "Federal Reserve")', "timespan": "3months"},
    {"name": "cnbc_bonds", "query": 'domain:cnbc.com (bond OR Treasuries OR "interest rates")', "timespan": "3months"},
    {"name": "mw_treasury", "query": 'domain:marketwatch.com (treasury OR FOMC OR yields OR Fed)', "timespan": "3months"},
    {"name": "mw_bonds", "query": 'domain:marketwatch.com (bond OR Treasuries OR "interest rates")', "timespan": "3months"},
    {"name": "investing_eco", "query": 'domain:investing.com (treasury OR inflation OR Fed OR yields)', "timespan": "3months"},
    {"name": "investing_bonds", "query": 'domain:investing.com (bond OR Treasuries OR "interest rate")', "timespan": "3months"},
    {"name": "reuters_fed", "query": 'domain:reuters.com (treasury OR FOMC OR "Federal Reserve" OR yields)', "timespan": "3months"},
    {"name": "reuters_bonds", "query": 'domain:reuters.com (bond OR Treasuries OR "interest rates")', "timespan": "3months"},
    {"name": "yahoo_fed", "query": 'domain:finance.yahoo.com (treasury OR FOMC OR Fed OR yields)', "timespan": "3months"},
    {"name": "yahoo_bonds", "query": 'domain:yahoo.com (Treasury OR "bond yields" OR FOMC)', "timespan": "3months"},
    {"name": "all_fomc", "query": '(FOMC OR "federal funds" OR "rate decision") (domain:cnbc.com OR domain:marketwatch.com OR domain:reuters.com)', "timespan": "3months"},
    {"name": "all_cpi", "query": '(CPI OR inflation OR PCE) (domain:cnbc.com OR domain:marketwatch.com OR domain:investing.com OR domain:reuters.com)', "timespan": "3months"},
    {"name": "all_auction", "query": '("Treasury auction" OR "debt ceiling" OR "Treasury supply") sourcelang:english', "timespan": "3months"},
    {"name": "all_10y", "query": '("10-year yield" OR "10-year Treasury" OR "2-year Treasury") sourcelang:english', "timespan": "3months"},
    {"name": "cnbc_1m", "query": "domain:cnbc.com (treasury OR Fed OR yields)", "timespan": "1month"},
    {"name": "mw_1m", "query": "domain:marketwatch.com (treasury OR Fed OR yields)", "timespan": "1month"},
    {"name": "reuters_1m", "query": "domain:reuters.com (treasury OR Fed OR yields)", "timespan": "1month"},
    {"name": "yahoo_1m", "query": "domain:finance.yahoo.com (treasury OR Fed OR yields)", "timespan": "1month"},
    {"name": "investing_1m", "query": "domain:investing.com (treasury OR Fed OR yields)", "timespan": "1month"},
    {"name": "week_hot", "query": '(treasury OR FOMC OR yields) (domain:cnbc.com OR domain:marketwatch.com OR domain:reuters.com OR domain:finance.yahoo.com)', "timespan": "7d"},
]


def _fetch_timespan(
    query: str,
    timespan: str,
    *,
    session: requests.Session,
    maxrecords: int = 250,
) -> list[dict]:
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": maxrecords,
        "format": "json",
        "timespan": timespan,
        "sort": "DateDesc",
    }
    for attempt in range(5):
        resp = session.get(GDELT_DOC_URL, params=params, timeout=90)
        if resp.status_code == 429:
            wait = 10 + attempt * 6
            print(f"[gdelt_bulk] 429 retry {attempt + 1} sleep {wait}s")
            time.sleep(wait)
            continue
        if resp.status_code != 200 or not resp.text.strip().startswith("{"):
            print(f"[gdelt_bulk] bad response HTTP {resp.status_code}: {resp.text[:100]}")
            return []
        try:
            payload = json.loads(resp.text)
        except json.JSONDecodeError:
            return []
        records: list[dict] = []
        for art in payload.get("articles") or []:
            url = art.get("url") or ""
            title = art.get("title") or ""
            if not title and not url:
                continue
            domain = art.get("domain")
            records.append(
                article_record(
                    source=_map_source(domain),
                    headline=title,
                    url=url,
                    published_at_utc=_parse_seendate(art.get("seendate")),
                    body=None,
                    section=domain,
                    tag=f"gdelt:{timespan}",
                    ingest_method="gdelt",
                )
            )
        return records
    return []


def fetch_gdelt_timespan_bulk(
    queries: list[dict] | None = None,
    *,
    sleep_seconds: float = 7.0,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    sess = session or make_session()
    queries = queries or TIMESPAN_QUERIES
    all_records: list[dict] = []
    # Cool down before first call
    time.sleep(8)
    for i, q in enumerate(queries, start=1):
        batch = _fetch_timespan(
            q["query"],
            q.get("timespan", "3months"),
            session=sess,
        )
        all_records.extend(batch)
        print(
            f"[gdelt_bulk] {i}/{len(queries)} {q['name']} "
            f"n={len(batch)} raw_total={len(all_records)}"
        )
        time.sleep(sleep_seconds)
    return records_to_frame(all_records)
