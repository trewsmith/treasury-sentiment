"""
Resumable GDELT DOC headline backfill for professional news (2025-01-01 onward).

Every (query, window) response is cached in data/raw/news/gdelt_windows/, so an interrupted run
resumes and failed windows are retried on the next run (failures are never cached as empty).
GDELT `seendate` is when GDELT first saw the article, at or after publication, so it does not
introduce look-ahead. Headlines only (no bodies).

Usage: PYTHONPATH=. python src/ingestion/news/gdelt_backfill.py [--start 2025-01-01] [--end ...]
Output: data/raw/news/gdelt_windows/*.json; merge with src/ingestion/news/merge_history.py
"""
from __future__ import annotations

import argparse
import json
import time

import pandas as pd
import requests

from src.ingestion.news.gdelt import GDELT_DOC_URL, _map_source, _parse_seendate
from src.ingestion.news.http_util import make_session
from src.ingestion.news.schema import article_record, records_to_frame
from src.utils.paths import NEWS_RAW_DIR

CACHE = NEWS_RAW_DIR / "gdelt_windows"
MAX = 250
QUERIES = {
    "rates": '("treasury yields" OR "treasury yield" OR "bond yields" OR "10-year treasury" OR "federal reserve" OR FOMC OR "interest rates") '
             "(domain:cnbc.com OR domain:marketwatch.com OR domain:reuters.com OR domain:investing.com OR domain:finance.yahoo.com)",
    "macro": '(inflation OR payrolls OR "jobs report" OR "treasury auction" OR "debt ceiling" OR recession) '
             "(domain:cnbc.com OR domain:marketwatch.com OR domain:reuters.com OR domain:investing.com)",
}


def fetch(sess, query, start, end):
    """Article list, or None on failure (so the window is retried later)."""
    p = dict(query=query, mode="ArtList", maxrecords=MAX, format="json",
             startdatetime=start.strftime("%Y%m%d%H%M%S"), enddatetime=end.strftime("%Y%m%d%H%M%S"))
    for attempt in range(5):
        try:
            r = sess.get(GDELT_DOC_URL, params=p, timeout=90)
        except requests.RequestException as exc:
            print(f"  {type(exc).__name__}", flush=True)
            time.sleep(60)
            continue
        if r.status_code == 200:
            t = r.text.strip()
            if t.startswith("{"):
                try:
                    return json.loads(t, strict=False).get("articles") or []
                except json.JSONDecodeError:
                    return None
            if "limit requests" not in t.lower():
                print(f"  non-json: {t[:100]}", flush=True)
                return None
        print(f"  throttled (HTTP {r.status_code})", flush=True)
        time.sleep(60 + 30 * attempt)
    return None


def backfill(start, end, days, sleep, queries):
    CACHE.mkdir(parents=True, exist_ok=True)
    sess = make_session()
    edges = list(pd.date_range(start, end, freq=f"{days}D"))
    failed = 0
    for name, q in ((k, QUERIES[k]) for k in queries):  # finish the core query before starting the next
        for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
            path = CACHE / f"{name}_{a:%Y%m%d}_{b:%Y%m%d}.json"
            if path.exists():
                continue
            arts = fetch(sess, q, a, b)
            if arts is None:
                failed += 1
            else:
                path.write_text(json.dumps(arts))
            print(f"{i + 1}/{len(edges) - 1} {name} {a:%Y-%m-%d} n={'FAIL' if arts is None else len(arts)}", flush=True)
            time.sleep(sleep)
    print(f"done; failed windows: {failed}")


def load_cached() -> pd.DataFrame:
    recs = []
    for path in sorted(CACHE.glob("*.json")):
        for a in json.loads(path.read_text()):
            if a.get("title") and a.get("url"):
                recs.append(article_record(
                    source=_map_source(a.get("domain")), headline=a["title"], url=a["url"],
                    published_at_utc=_parse_seendate(a.get("seendate")), section=a.get("domain"),
                    tag="gdelt_backfill", ingest_method="gdelt"))
    return records_to_frame(recs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2025-01-01")
    ap.add_argument("--end", default=pd.Timestamp.now("UTC").strftime("%Y-%m-%d"))
    ap.add_argument("--days", type=int, default=4)
    ap.add_argument("--sleep", type=float, default=15.0)
    ap.add_argument("--queries", nargs="+", default=list(QUERIES), choices=list(QUERIES))
    a = ap.parse_args()
    backfill(a.start, a.end, a.days, a.sleep, a.queries)
