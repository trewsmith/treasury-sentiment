"""
Polite listing-page collectors for publishers where RSS history is thin.

Only used for public section/topic pages (CNBC, Yahoo Finance).
MarketWatch/Investing listing pages currently block anonymous scrapers (401/403).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.ingestion.news.http_util import make_session
from src.ingestion.news.schema import article_record, records_to_frame

CNBC_SECTIONS = [
    ("https://www.cnbc.com/economy/", "economy"),
    ("https://www.cnbc.com/finance/", "finance"),
    ("https://www.cnbc.com/investing/", "investing"),
    ("https://www.cnbc.com/bonds/", "bonds"),
    ("https://www.cnbc.com/federal-reserve/", "federal_reserve"),
]

YAHOO_TOPICS = [
    ("https://finance.yahoo.com/topic/economic-news/", "economic-news"),
    ("https://finance.yahoo.com/topic/stock-market-news/", "stock-market-news"),
    ("https://finance.yahoo.com/topic/latest-news/", "latest-news"),
]


def _cnbc_date_from_url(url: str) -> datetime | None:
    m = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if not m:
        return None
    try:
        return datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc
        )
    except ValueError:
        return None


def fetch_cnbc_listings(session: requests.Session | None = None) -> pd.DataFrame:
    sess = session or make_session()
    records: list[dict] = []
    seen: set[str] = set()

    for url, section in CNBC_SECTIONS:
        try:
            resp = sess.get(url, timeout=40)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[listings] cnbc/{section} failed: {exc}")
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        n_before = len(records)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full = urljoin("https://www.cnbc.com", href)
            if "cnbc.com" not in full or "/20" not in full:
                continue
            if full in seen:
                continue
            headline = a.get_text(" ", strip=True)
            if not headline or len(headline) < 20:
                continue
            seen.add(full)
            records.append(
                article_record(
                    source="cnbc",
                    headline=headline,
                    url=full,
                    published_at_utc=_cnbc_date_from_url(full),
                    body=None,
                    section=section,
                    tag="listing",
                    ingest_method="listing",
                )
            )
        print(f"[listings] cnbc/{section} -> {len(records) - n_before}")

    return records_to_frame(records)


def fetch_yahoo_listings(session: requests.Session | None = None) -> pd.DataFrame:
    sess = session or make_session()
    # Yahoo often wants a browser-like UA
    sess.headers["User-Agent"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    records: list[dict] = []
    seen: set[str] = set()

    for url, section in YAHOO_TOPICS:
        try:
            resp = sess.get(url, timeout=40)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[listings] yahoo/{section} failed: {exc}")
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        n_before = len(records)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full = urljoin("https://finance.yahoo.com", href)
            if "finance.yahoo.com" not in full:
                continue
            if not any(x in full for x in ("/news/", "/article", "/economy/", "/video/")):
                continue
            if full in seen:
                continue
            headline = a.get_text(" ", strip=True)
            if not headline or len(headline) < 25:
                continue
            seen.add(full)
            records.append(
                article_record(
                    source="yahoo_finance",
                    headline=headline,
                    url=full,
                    published_at_utc=None,
                    body=None,
                    section=section,
                    tag="listing",
                    ingest_method="listing",
                )
            )
        print(f"[listings] yahoo/{section} -> {len(records) - n_before}")

    return records_to_frame(records)


def fetch_listings(session: requests.Session | None = None) -> pd.DataFrame:
    sess = session or make_session()
    frames = [fetch_cnbc_listings(sess), fetch_yahoo_listings(sess)]
    frames = [f for f in frames if f is not None and not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else records_to_frame([])
