"""Federal Reserve press releases, speeches, and testimony (official JSON)."""

from __future__ import annotations

import json
from datetime import datetime
from html import unescape
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from src.ingestion.news.http_util import get_bytes, make_session
from src.ingestion.news.schema import article_record, records_to_frame

FED_TZ = ZoneInfo("America/New_York")
FED_BASE = "https://www.federalreserve.gov"


def _parse_fed_datetime(raw: str) -> datetime | None:
    """Parse Fed timestamps like '10/16/2026 11:00:00 AM' as US Eastern -> UTC."""
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y"):
        try:
            local = datetime.strptime(raw, fmt).replace(tzinfo=FED_TZ)
            return local.astimezone(ZoneInfo("UTC"))
        except ValueError:
            continue
    return None


def fetch_fed_json_sources(
    sources: list[dict],
    *,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    sess = session or make_session()
    records: list[dict] = []

    for src in sources:
        name = src["name"]
        url = src["url"]
        try:
            raw = get_bytes(url, session=sess, timeout=60)
            data = json.loads(raw.decode("utf-8-sig"))
        except Exception as exc:
            print(f"[fed] failed {name}: {exc}")
            continue

        for row in data:
            path = row.get("l") or ""
            full_url = path if path.startswith("http") else f"{FED_BASE}{path}"
            section = row.get(src.get("section_field", ""), None) or src.get("section")
            tag = row.get("s") or section  # speaker for speeches/testimony
            headline = unescape(row.get("t") or "")
            records.append(
                article_record(
                    source="federal_reserve",
                    headline=headline,
                    url=full_url,
                    published_at_utc=_parse_fed_datetime(row.get("d", "")),
                    body=None,
                    section=section,
                    tag=tag,
                    ingest_method="fed_json",
                )
            )
        print(f"[fed] {name} -> {len(data)}")

    return records_to_frame(records)
