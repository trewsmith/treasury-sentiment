"""
Canonical document schema shared by news and Reddit.

Every text observation becomes one row:
  doc_id, source_type, source_name, timestamp_utc, headline, body, text, meta
plus derived time-alignment / analysis columns (see DOCUMENT_COLUMNS).
`meta` is a JSON string of source-specific fields; use `expand_meta` to flatten it.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from src.cleaning.text import (
    body_repeats_headline,
    clean_text,
    drop_leading_headline,
    is_missing,
    split_gnews_publisher,
)

CANONICAL_COLUMNS = [
    "doc_id",
    "source_type",
    "source_name",
    "timestamp_utc",
    "headline",
    "body",
    "text",
    "meta",
]

DERIVED_COLUMNS = [
    "timestamp_et",
    "et_date",
    "market_session",
    "yield_date",
    "timestamp_is_date_only",
    "n_words",
    "text_hash",
]

DOCUMENT_COLUMNS = CANONICAL_COLUMNS + DERIVED_COLUMNS

NEWS_META_FIELDS = ["article_id", "url", "section", "tag", "ingest_method", "collected_at_utc"]
REDDIT_META_FIELDS = [
    "post_id",
    "subreddit",
    "author",
    "score",
    "upvote_ratio",
    "num_comments",
    "permalink",
    "url",
    "domain",
    "is_self",
    "link_flair_text",
    "over_18",
    "crosspost_parent",
    "ingest_method",
    "score_observed_at_utc",
]


def _json_value(val: Any) -> Any:
    if is_missing(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.isoformat()
    if hasattr(val, "item"):  # numpy scalars
        return val.item()
    return val


def _meta_json(fields: dict[str, Any]) -> str:
    return json.dumps({k: _json_value(v) for k, v in fields.items()}, sort_keys=True)


def _join_text(headline: str, body: str) -> str:
    return f"{headline}\n\n{body}" if body else headline


def _clean_pair(headline: str, body: str) -> tuple[str, str]:
    if body:
        body = drop_leading_headline(headline, body)
    if body and body_repeats_headline(headline, body):
        body = ""
    return headline, body


def news_to_documents(news: pd.DataFrame) -> pd.DataFrame:
    """news_raw.parquet rows → canonical documents (no filtering)."""
    rows = []
    for rec in news.to_dict("records"):
        headline = clean_text(rec.get("headline"))
        publisher = None
        if rec.get("source") == "google_news":
            headline, publisher = split_gnews_publisher(headline)
        headline, body = _clean_pair(headline, clean_text(rec.get("body"), repair_bare_a=True))
        meta = {k: rec.get(k) for k in NEWS_META_FIELDS}
        meta["publisher"] = publisher
        rows.append(
            {
                "doc_id": f"news:{rec['article_id']}",
                "source_type": "news",
                "source_name": rec.get("source"),
                "timestamp_utc": rec.get("published_at_utc"),
                "headline": headline,
                "body": body or None,
                "text": _join_text(headline, body),
                "meta": _meta_json(meta),
            }
        )
    return _to_frame(rows)


def reddit_to_documents(posts: pd.DataFrame) -> pd.DataFrame:
    """reddit_posts_raw.parquet rows → canonical documents (no filtering)."""
    rows = []
    for rec in posts.to_dict("records"):
        headline = clean_text(rec.get("title"))
        headline, body = _clean_pair(headline, clean_text(rec.get("selftext"), markdown=True))
        rows.append(
            {
                "doc_id": f"reddit:{rec['post_id']}",
                "source_type": "reddit",
                "source_name": f"r/{rec.get('subreddit')}",
                "timestamp_utc": rec.get("created_utc"),
                "headline": headline,
                "body": body or None,
                "text": _join_text(headline, body),
                "meta": _meta_json({k: rec.get(k) for k in REDDIT_META_FIELDS}),
            }
        )
    return _to_frame(rows)


def _to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=CANONICAL_COLUMNS)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, errors="coerce").astype(
        "datetime64[us, UTC]"
    )
    return df


def expand_meta(df: pd.DataFrame, prefix: str = "meta_") -> pd.DataFrame:
    """
    Return df with the JSON `meta` column flattened into `meta_<key>` columns.

    Keys missing for a source (e.g. `score` on news rows) become null.
    """
    parsed = pd.json_normalize(df["meta"].map(json.loads).tolist())
    parsed.index = df.index
    return pd.concat([df, parsed.add_prefix(prefix)], axis=1)
