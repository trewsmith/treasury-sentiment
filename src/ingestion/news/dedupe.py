"""News de-duplication pipeline."""

from __future__ import annotations

import pandas as pd

from src.ingestion.news.schema import ARTICLE_COLUMNS, content_hash, normalize_url


def _body_len(val) -> int:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0
    return len(str(val))


def dedupe_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate news articles.

    Stages:
      1. Normalize URLs
      2. Drop exact article_id duplicates (prefer rows with longer body)
      3. Drop near-duplicates with same normalized headline + calendar day
    """
    if df.empty:
        return df.copy()

    out = df.copy()
    out["url"] = out["url"].map(normalize_url)
    out["_body_len"] = out["body"].map(_body_len)
    out["_has_body"] = out["_body_len"] > 0

    # Prefer richer records when collapsing
    out = out.sort_values(
        by=["_has_body", "_body_len", "collected_at_utc"],
        ascending=[False, False, False],
    )

    before = len(out)
    out = out.drop_duplicates(subset=["article_id"], keep="first")
    after_id = len(out)

    out["_content_hash"] = [
        content_hash(h, p)
        for h, p in zip(out["headline"], out["published_at_utc"], strict=False)
    ]
    # Only collapse content-hash dupes when headline is non-empty
    nonempty = out["headline"].fillna("").str.strip() != ""
    dup_mask = out.duplicated(subset=["_content_hash"], keep="first") & nonempty
    out = out.loc[~dup_mask].copy()
    after_content = len(out)

    print(
        f"[dedupe] {before} → {after_id} (article_id) → {after_content} (headline+day)"
    )

    out = out.drop(columns=["_body_len", "_has_body", "_content_hash"], errors="ignore")
    for col in ARTICLE_COLUMNS:
        if col not in out.columns:
            out[col] = None
    return out[ARTICLE_COLUMNS].reset_index(drop=True)
