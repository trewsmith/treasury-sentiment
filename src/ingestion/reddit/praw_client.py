"""
Optional PRAW (official Reddit API) backend for the most recent posts.

Reddit listings return at most ~1000 submissions per subreddit, so this cannot
backfill history; it tops up the days the archive has not caught up on yet.

Requires in .env (script-type app: https://www.reddit.com/prefs/apps):
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

from src.ingestion.reddit.schema import empty_posts_frame, post_record, records_to_frame
from src.utils.paths import PROJECT_ROOT

ENV_VARS = ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT")


def get_credentials() -> dict[str, str] | None:
    """Return PRAW credentials from the environment / .env, or None if incomplete."""
    load_dotenv(PROJECT_ROOT / ".env")
    creds = {k: os.getenv(k, "").strip() for k in ENV_VARS}
    if any(not v or v.startswith("your_") for v in creds.values()):
        return None
    return creds


def _submission_to_dict(sub) -> dict:
    return {
        "id": sub.id,
        "subreddit": sub.subreddit.display_name,
        "title": sub.title,
        "selftext": sub.selftext,
        "author": sub.author.name if sub.author is not None else "[deleted]",
        "score": sub.score,
        "upvote_ratio": getattr(sub, "upvote_ratio", None),
        "num_comments": sub.num_comments,
        "created_utc": sub.created_utc,
        "permalink": sub.permalink,
        "url": sub.url,
        "domain": getattr(sub, "domain", None),
        "is_self": sub.is_self,
        "link_flair_text": getattr(sub, "link_flair_text", None),
        "over_18": sub.over_18,
        "stickied": sub.stickied,
        "distinguished": getattr(sub, "distinguished", None),
        "removed_by_category": getattr(sub, "removed_by_category", None),
        "crosspost_parent": getattr(sub, "crosspost_parent", None),
    }


def fetch_recent_posts(
    subreddits: list[str],
    *,
    limit_per_subreddit: int = 1000,
    since: datetime | None = None,
) -> pd.DataFrame:
    """Newest submissions per subreddit via PRAW (read-only). Empty frame if no credentials."""
    creds = get_credentials()
    if creds is None:
        print("[praw] REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET / REDDIT_USER_AGENT not set; skipping")
        return empty_posts_frame()

    import praw  # imported lazily so the archive backend works without praw installed

    reddit = praw.Reddit(
        client_id=creds["REDDIT_CLIENT_ID"],
        client_secret=creds["REDDIT_CLIENT_SECRET"],
        user_agent=creds["REDDIT_USER_AGENT"],
    )
    reddit.read_only = True

    records = []
    for name in subreddits:
        observed = datetime.now(timezone.utc)
        n = 0
        for sub in reddit.subreddit(name).new(limit=limit_per_subreddit):
            if since is not None and sub.created_utc < since.timestamp():
                break  # `new` is newest-first
            records.append(
                post_record(
                    _submission_to_dict(sub),
                    ingest_method="praw",
                    score_observed_at_utc=observed,
                    collected_at_utc=observed,
                )
            )
            n += 1
        print(f"  r/{name}: {n:,} posts (praw)")
    return records_to_frame(records) if records else empty_posts_frame()
