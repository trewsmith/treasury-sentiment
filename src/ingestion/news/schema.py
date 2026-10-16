"""Canonical news article schema and identifiers."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import pandas as pd

ARTICLE_COLUMNS = [
    "article_id",
    "source",
    "headline",
    "body",
    "published_at_utc",
    "url",
    "section",
    "tag",
    "ingest_method",
    "collected_at_utc",
]

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "mc_cid",
    "mc_eid",
    "fbclid",
    "gclid",
    "ncid",
    "ref",
    "sref",
    "mod",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    url = url.strip()
    parsed = urlparse(url)
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/") or "/"
    query_pairs = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() not in TRACKING_PARAMS
    ]
    query = urlencode(sorted(query_pairs))
    return urlunparse((scheme, netloc, path, "", query, ""))


def normalize_headline(headline: str | None) -> str:
    if not headline:
        return ""
    text = re.sub(r"\s+", " ", headline).strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def make_article_id(url: str | None, headline: str | None = None) -> str:
    """Stable id: prefer normalized URL hash; fall back to headline."""
    norm_url = normalize_url(url)
    basis = norm_url or normalize_headline(headline)
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:32]


def content_hash(headline: str | None, published_at_utc: Any = None) -> str:
    day = ""
    if published_at_utc is not None and not pd.isna(published_at_utc):
        day = pd.Timestamp(published_at_utc).strftime("%Y-%m-%d")
    basis = f"{normalize_headline(headline)}|{day}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:32]


def empty_articles_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=ARTICLE_COLUMNS)


def article_record(
    *,
    source: str,
    headline: str,
    url: str,
    published_at_utc: datetime | pd.Timestamp | None = None,
    body: str | None = None,
    section: str | None = None,
    tag: str | None = None,
    ingest_method: str = "rss",
    collected_at_utc: datetime | None = None,
) -> dict[str, Any]:
    pub = pd.to_datetime(published_at_utc, utc=True, errors="coerce")
    return {
        "article_id": make_article_id(url, headline),
        "source": source,
        "headline": (headline or "").strip(),
        "body": (body or "").strip() or None,
        "published_at_utc": pub,
        "url": normalize_url(url) or (url or ""),
        "section": section,
        "tag": tag,
        "ingest_method": ingest_method,
        "collected_at_utc": collected_at_utc or utc_now(),
    }


def records_to_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return empty_articles_frame()
    df = pd.DataFrame(records)
    for col in ARTICLE_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[ARTICLE_COLUMNS]
    df["published_at_utc"] = pd.to_datetime(df["published_at_utc"], utc=True, errors="coerce")
    df["collected_at_utc"] = pd.to_datetime(df["collected_at_utc"], utc=True, errors="coerce")
    return df
