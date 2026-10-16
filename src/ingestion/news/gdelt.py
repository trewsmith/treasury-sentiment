"""
GDELT DOC 2.1 historical article lists.

Free, no API key. Rate-limit ~1 request / 5+ seconds.
Returns headlines + URLs + seen dates (not full article bodies).
Used to cover Yahoo/Reuters/CNBC/MarketWatch/Investing history without
brittle site scraping.

Note: the DOC API is most reliable for roughly the last ~3 months.
Older windows are attempted best-effort and may return sparse/empty results.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable

import pandas as pd
import requests

from src.ingestion.news.http_util import make_session
from src.ingestion.news.schema import article_record, records_to_frame

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

DOMAIN_TO_SOURCE = {
    "cnbc.com": "cnbc",
    "marketwatch.com": "marketwatch",
    "investing.com": "investing",
    "reuters.com": "reuters",
    "finance.yahoo.com": "yahoo_finance",
    "yahoo.com": "yahoo_finance",
    "seekingalpha.com": "seeking_alpha",
    "theguardian.com": "guardian",
    "federalreserve.gov": "federal_reserve",
}


def _map_source(domain: str | None) -> str:
    domain = (domain or "").lower().removeprefix("www.")
    for key, source in DOMAIN_TO_SOURCE.items():
        if domain == key or domain.endswith("." + key):
            return source
    return domain or "gdelt"


def _parse_seendate(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _daterange_windows(
    start: datetime,
    end: datetime,
    window_days: int,
) -> Iterable[tuple[datetime, datetime]]:
    cur = start
    delta = timedelta(days=window_days)
    while cur < end:
        nxt = min(cur + delta, end)
        yield cur, nxt
        cur = nxt


def fetch_gdelt_window(
    query: str,
    start: datetime,
    end: datetime,
    *,
    maxrecords: int = 250,
    session: requests.Session | None = None,
    max_retries: int = 6,
) -> list[dict]:
    sess = session or make_session()
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": maxrecords,
        "format": "json",
        "startdatetime": start.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end.strftime("%Y%m%d%H%M%S"),
    }

    resp = None
    for attempt in range(max_retries):
        resp = sess.get(GDELT_DOC_URL, params=params, timeout=90)
        if resp.status_code == 429:
            wait = 8 + attempt * 5
            print(
                f"[gdelt] 429 {start.date()}→{end.date()} "
                f"retry {attempt + 1}/{max_retries} sleep {wait}s"
            )
            time.sleep(wait)
            continue
        break

    if resp is None or resp.status_code != 200:
        code = None if resp is None else resp.status_code
        print(f"[gdelt] HTTP {code} for {start.date()}–{end.date()}")
        return []

    text = resp.text.strip()
    if not text.startswith("{"):
        # Empty result sets sometimes come back as plain text
        if "No articles" in text or text == "":
            return []
        print(f"[gdelt] non-json for {start.date()}–{end.date()}: {text[:120]}")
        return []

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        print(f"[gdelt] json decode failed for {start.date()}–{end.date()}")
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
                tag="gdelt",
                ingest_method="gdelt",
            )
        )
    return records


def fetch_gdelt_history(
    queries: list[dict],
    *,
    start: datetime,
    end: datetime | None = None,
    window_days: int = 3,
    maxrecords: int = 250,
    sleep_seconds: float = 6.0,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Sweep non-overlapping date windows for each configured GDELT query."""
    sess = session or make_session()
    end = end or datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    all_records: list[dict] = []
    windows = list(_daterange_windows(start, end, window_days))
    total = max(len(windows) * len(queries), 1)
    done = 0

    # Newest-first tends to be more reliable on the DOC API
    windows = list(reversed(windows))

    for q in queries:
        name = q.get("name", "query")
        query = q["query"]
        for w_start, w_end in windows:
            batch = fetch_gdelt_window(
                query,
                w_start,
                w_end,
                maxrecords=maxrecords,
                session=sess,
            )
            all_records.extend(batch)
            done += 1
            print(
                f"[gdelt] {done}/{total} | {name} {w_start.date()}→{w_end.date()} "
                f"n={len(batch)} | raw_total={len(all_records)}"
            )
            time.sleep(sleep_seconds)

    return records_to_frame(all_records)
