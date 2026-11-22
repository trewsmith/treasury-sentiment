"""
Arctic Shift (Pushshift successor) client for historical Reddit submissions.

API: https://github.com/ArthurHeitmann/arctic_shift/blob/master/api/README.md

Pulls are chunked by (subreddit, calendar month, UTC) and cached as parquet
under data/raw/reddit/arctic_shift/<subreddit>/<YYYY-MM>.parquet so long runs
can resume. Months that ended more than `cache_after_days` ago are treated as
final and reused; the current month is always re-pulled.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.ingestion.news.http_util import make_session
from src.ingestion.reddit.schema import empty_posts_frame, post_record, records_to_frame
from src.utils.paths import REDDIT_RAW_DIR

DEFAULT_BASE_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"
MAX_ATTEMPTS = 6


class ArcticShiftError(RuntimeError):
    pass


def _get_page(
    session: requests.Session,
    base_url: str,
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    """GET one page with retries on network errors, 429/5xx, and API 'Timeout' errors."""
    last_err: Exception | str | None = None
    for attempt in range(MAX_ATTEMPTS):
        if attempt:
            time.sleep(min(60, 2**attempt))
        try:
            resp = session.get(base_url, params=params, timeout=90)
        except requests.RequestException as exc:
            last_err = exc
            continue
        if resp.status_code in (422, 429) or resp.status_code >= 500:  # 422 is intermittent on this API
            last_err = f"HTTP {resp.status_code}"
            reset = resp.headers.get("x-ratelimit-reset")
            if resp.status_code == 429 and reset and reset.isdigit():
                time.sleep(min(120, int(reset)))
            continue
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("error"):
            # e.g. "Timeout. Maybe slow down a bit" — transient server-side load
            last_err = payload["error"]
            continue
        return payload.get("data") or []
    raise ArcticShiftError(f"Arctic Shift request failed after {MAX_ATTEMPTS} attempts: {last_err}")


def fetch_window(
    subreddit: str,
    start: datetime,
    end: datetime,
    *,
    session: requests.Session | None = None,
    base_url: str = DEFAULT_BASE_URL,
    page_size: int = 100,
    sleep_seconds: float = 0.5,
) -> pd.DataFrame:
    """
    All submissions in r/<subreddit> with start <= created_utc < end.

    Pages ascending by created_utc. The API's `after` bound is exclusive, so the
    cursor steps back one second each page to avoid dropping posts that share a
    timestamp with the page boundary; overlaps are removed by post id.
    """
    sess = session or make_session()
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())
    collected_at = datetime.now(timezone.utc)

    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    cursor = start_ts - 1
    while True:
        page = _get_page(
            sess,
            base_url,
            {
                "subreddit": subreddit,
                "after": cursor,
                "before": end_ts,
                "limit": page_size,
                "sort": "asc",
            },
        )
        if not page:
            break
        new = [p for p in page if p.get("id") and p["id"] not in seen]
        for raw in new:
            seen.add(raw["id"])
            records.append(
                post_record(raw, ingest_method="arctic_shift", collected_at_utc=collected_at)
            )
        last = max(int(p["created_utc"]) for p in page)
        # Overlap by one second while making progress; jump past `last` once a
        # page yields nothing new (`last` > cursor always, so this terminates).
        cursor = last - 1 if new else last
        if sleep_seconds:
            time.sleep(sleep_seconds)

    if not records:
        return empty_posts_frame()
    df = records_to_frame(records)
    in_window = (df["created_utc"] >= pd.Timestamp(start)) & (df["created_utc"] < pd.Timestamp(end))
    return df.loc[in_window].reset_index(drop=True)


def _month_start(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _next_month(dt: datetime) -> datetime:
    return _month_start(_month_start(dt) + timedelta(days=32))


def month_windows(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
    """Split [start, end) into calendar-month windows (UTC), clipped to the bounds."""
    windows = []
    cur = start
    while cur < end:
        nxt = _next_month(cur)
        windows.append((cur, min(nxt, end)))
        cur = nxt
    return windows


def _cache_path(subreddit: str, window_start: datetime, cache_dir: Path) -> Path:
    return cache_dir / subreddit.lower() / f"{window_start:%Y-%m}.parquet"


def fetch_subreddit_history(
    subreddit: str,
    start: datetime,
    end: datetime,
    *,
    session: requests.Session | None = None,
    base_url: str = DEFAULT_BASE_URL,
    page_size: int = 100,
    sleep_seconds: float = 0.5,
    cache_after_days: float = 3,
    refresh: bool = False,
    cache_dir: Path | None = None,
) -> pd.DataFrame:
    """Month-chunked, cached pull of every submission in [start, end)."""
    sess = session or make_session()
    cache_root = cache_dir or (REDDIT_RAW_DIR / "arctic_shift")
    final_before = datetime.now(timezone.utc) - timedelta(days=cache_after_days)

    frames = []
    for w_start, w_end in month_windows(start, end):
        path = _cache_path(subreddit, w_start, cache_root)
        # Only full calendar months are cached; a clipped first/last window is not
        is_full_month = w_start == _month_start(w_start) and w_end == _next_month(w_start)
        cacheable = is_full_month and w_end <= final_before
        if cacheable and path.exists() and not refresh:
            df = pd.read_parquet(path)
            print(f"  r/{subreddit} {w_start:%Y-%m}: {len(df):,} posts (cached)")
        else:
            df = fetch_window(
                subreddit,
                w_start,
                w_end,
                session=sess,
                base_url=base_url,
                page_size=page_size,
                sleep_seconds=sleep_seconds,
            )
            print(f"  r/{subreddit} {w_start:%Y-%m}: {len(df):,} posts")
            if cacheable:
                path.parent.mkdir(parents=True, exist_ok=True)
                tmp = path.with_suffix(".parquet.tmp")
                df.to_parquet(tmp, index=False)
                tmp.replace(path)  # atomic: an interrupted run never leaves a partial month
        frames.append(df)

    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else empty_posts_frame()
