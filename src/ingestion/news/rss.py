"""Generic RSS / Atom feed ingestion."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import requests

from src.ingestion.news.http_util import get_bytes, make_session
from src.ingestion.news.schema import article_record, records_to_frame


def _entry_datetime(entry: dict[str, Any]) -> datetime | None:
    for key in ("published", "updated", "created"):
        raw = entry.get(key)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _entry_body(entry: dict[str, Any]) -> str | None:
    if entry.get("content"):
        parts = [c.get("value", "") for c in entry["content"] if isinstance(c, dict)]
        text = " ".join(parts).strip()
        if text:
            return text
    summary = entry.get("summary") or entry.get("description")
    if summary:
        return str(summary).strip()
    return None


def fetch_rss_feed(
    url: str,
    *,
    source: str,
    section: str | None = None,
    session: requests.Session | None = None,
) -> list[dict]:
    sess = session or make_session()
    try:
        raw = get_bytes(url, session=sess, timeout=40)
    except Exception as exc:
        print(f"[rss] failed {source}/{section}: {exc}")
        return []

    parsed = feedparser.parse(raw)
    records: list[dict] = []
    for entry in parsed.entries:
        link = entry.get("link") or ""
        title = entry.get("title") or ""
        if not title and not link:
            continue
        tags = []
        for tag in entry.get("tags") or []:
            term = tag.get("term") if isinstance(tag, dict) else None
            if term:
                tags.append(term)
        records.append(
            article_record(
                source=source,
                headline=title,
                url=link,
                published_at_utc=_entry_datetime(entry),
                body=_entry_body(entry),
                section=section,
                tag=",".join(tags) if tags else section,
                ingest_method="rss",
            )
        )
    return records


def fetch_rss_feeds(
    feeds: list[dict],
    *,
    source: str,
    session: requests.Session | None = None,
):
    sess = session or make_session()
    all_records: list[dict] = []
    for feed in feeds:
        records = fetch_rss_feed(
            feed["url"],
            source=source,
            section=feed.get("section"),
            session=sess,
        )
        print(f"[rss] {source}/{feed.get('section')} -> {len(records)}")
        all_records.extend(records)
    return records_to_frame(all_records)
