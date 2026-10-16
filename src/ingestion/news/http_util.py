"""Shared HTTP helpers for news ingestion."""

from __future__ import annotations

import time
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; treasury-sentiment/0.1; "
        "academic-research; +https://github.com/local)"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, application/json, */*",
}


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


@retry(wait=wait_exponential(multiplier=1, min=1, max=20), stop=stop_after_attempt(4), reraise=True)
def get_bytes(
    url: str,
    *,
    session: requests.Session | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 45,
    sleep_s: float = 0.0,
) -> bytes:
    if sleep_s:
        time.sleep(sleep_s)
    sess = session or make_session()
    resp = sess.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.content


@retry(wait=wait_exponential(multiplier=1, min=1, max=20), stop=stop_after_attempt(4), reraise=True)
def get_text(
    url: str,
    *,
    session: requests.Session | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 45,
    sleep_s: float = 0.0,
) -> str:
    content = get_bytes(
        url, session=session, params=params, timeout=timeout, sleep_s=sleep_s
    )
    return content.decode("utf-8", errors="replace")
