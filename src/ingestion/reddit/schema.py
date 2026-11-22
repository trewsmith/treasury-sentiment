"""Canonical Reddit post schema."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.ingestion.news.schema import utc_now

REDDIT_POST_COLUMNS = [
    "post_id",
    "subreddit",
    "title",
    "selftext",
    "author",
    "score",
    "upvote_ratio",
    "num_comments",
    "created_utc",
    "permalink",
    "url",
    "domain",
    "is_self",
    "link_flair_text",
    "over_18",
    "stickied",
    "distinguished",
    "removed_by_category",
    "crosspost_parent",
    "ingest_method",
    "score_observed_at_utc",
    "collected_at_utc",
]

TIMESTAMP_COLUMNS = ["created_utc", "score_observed_at_utc", "collected_at_utc"]
INT_COLUMNS = ["score", "num_comments"]
BOOL_COLUMNS = ["is_self", "over_18", "stickied"]


def _str_or_none(val: Any) -> str | None:
    if val is None:
        return None
    text = str(val).strip()
    return text or None


def _epoch_to_utc(val: Any) -> pd.Timestamp:
    if val is None or val == "":
        return pd.NaT
    return pd.to_datetime(float(val), unit="s", utc=True, errors="coerce")


def make_permalink(subreddit: str, post_id: str) -> str:
    return f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/"


def post_record(
    raw: dict[str, Any],
    *,
    ingest_method: str,
    score_observed_at_utc: Any = None,
    collected_at_utc: Any = None,
) -> dict[str, Any]:
    """
    Normalize one Reddit submission (Arctic Shift JSON or PRAW-derived dict).

    `score_observed_at_utc` records when score / num_comments were captured:
    archive snapshots are typically ~36h after posting, so scores are not
    comparable to a fresh PRAW pull.
    """
    post_id = str(raw["id"]).removeprefix("t3_")
    subreddit = str(raw.get("subreddit") or "")
    permalink = raw.get("permalink")
    permalink = (
        f"https://www.reddit.com{permalink}"
        if permalink and str(permalink).startswith("/")
        else _str_or_none(permalink) or make_permalink(subreddit, post_id)
    )
    observed = score_observed_at_utc
    if observed is None:
        # Arctic Shift stores the post seconds after creation (`retrieved_on`) and
        # refreshes score / num_comments on a second pass (~36h later), recorded in
        # `_meta.retrieved_2nd_on`. The stored score belongs to the latest pass.
        meta = raw.get("_meta") or {}
        retrieved = meta.get("retrieved_2nd_on") or raw.get("retrieved_on")
        if retrieved:
            observed = _epoch_to_utc(retrieved)
    return {
        "post_id": post_id,
        "subreddit": subreddit.lower(),
        "title": (raw.get("title") or "").strip(),
        "selftext": _str_or_none(raw.get("selftext")),
        "author": _str_or_none(raw.get("author")),
        "score": raw.get("score"),
        "upvote_ratio": raw.get("upvote_ratio"),
        "num_comments": raw.get("num_comments"),
        "created_utc": _epoch_to_utc(raw.get("created_utc")),
        "permalink": permalink,
        "url": _str_or_none(raw.get("url")),
        "domain": _str_or_none(raw.get("domain")),
        "is_self": raw.get("is_self"),
        "link_flair_text": _str_or_none(raw.get("link_flair_text")),
        "over_18": raw.get("over_18"),
        "stickied": raw.get("stickied"),
        "distinguished": _str_or_none(raw.get("distinguished")),
        "removed_by_category": _str_or_none(raw.get("removed_by_category")),
        "crosspost_parent": _str_or_none(raw.get("crosspost_parent")),
        "ingest_method": ingest_method,
        "score_observed_at_utc": observed,
        "collected_at_utc": collected_at_utc or utc_now(),
    }


def empty_posts_frame() -> pd.DataFrame:
    return records_to_frame([])


def records_to_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    for col in REDDIT_POST_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[REDDIT_POST_COLUMNS]
    for col in TIMESTAMP_COLUMNS:
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    for col in INT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    df["upvote_ratio"] = pd.to_numeric(df["upvote_ratio"], errors="coerce").astype("float64")
    for col in BOOL_COLUMNS:
        df[col] = df[col].astype("boolean")
    return df
