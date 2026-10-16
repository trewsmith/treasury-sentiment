"""Best-effort article body enrichment via trafilatura."""

from __future__ import annotations

import time

import pandas as pd
import requests
import trafilatura

from src.ingestion.news.http_util import make_session


def fetch_article_body(
    url: str,
    *,
    session: requests.Session | None = None,
    timeout: int = 30,
) -> str | None:
    sess = session or make_session()
    try:
        resp = sess.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception:
        return None
    text = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
    if text and len(text.strip()) >= 40:
        return text.strip()
    return None


def enrich_bodies(
    df: pd.DataFrame,
    *,
    max_articles: int = 2500,
    sleep_seconds: float = 0.4,
    source_priority: list[str] | None = None,
) -> pd.DataFrame:
    """
    Fill missing bodies for up to max_articles rows.

    Priority: configured source order, then prefer federal_reserve monetary /
    speech / testimony, then rows still missing bodies.
    """
    if df.empty or max_articles <= 0:
        return df

    out = df.copy()
    if "body" not in out.columns:
        out["body"] = None

    missing = out["body"].isna() | (out["body"].astype(str).str.len() < 40)
    candidates = out.loc[missing].copy()

    priority = source_priority or [
        "federal_reserve",
        "cnbc",
        "marketwatch",
        "investing",
        "reuters",
        "yahoo_finance",
    ]
    rank = {s: i for i, s in enumerate(priority)}
    candidates["_src_rank"] = candidates["source"].map(lambda s: rank.get(s, 99))

    # Prefer Fed monetary / speech / testimony for research relevance
    def _fed_boost(row) -> int:
        if row.get("source") != "federal_reserve":
            return 1
        section = str(row.get("section") or "").lower()
        if any(k in section for k in ("monetary", "speech", "testimony", "fomc")):
            return 0
        if "enforcement" in section:
            return 2
        return 1

    candidates["_fed_boost"] = candidates.apply(_fed_boost, axis=1)
    candidates = candidates.sort_values(
        ["_fed_boost", "_src_rank", "published_at_utc"],
        ascending=[True, True, False],
    )

    targets = candidates.head(max_articles)
    session = make_session()
    filled = 0
    attempted = 0

    for idx, row in targets.iterrows():
        url = row.get("url")
        if not url:
            continue
        # Google News links are redirect wrappers; skip body fetch
        if "news.google.com" in str(url):
            continue
        attempted += 1
        body = fetch_article_body(url, session=session)
        if body:
            out.at[idx, "body"] = body
            filled += 1
        if attempted % 50 == 0:
            print(f"[enrich] attempted={attempted}/{len(targets)} filled={filled}")
        time.sleep(sleep_seconds)

    print(f"[enrich] done attempted={attempted} filled={filled}")
    return out
