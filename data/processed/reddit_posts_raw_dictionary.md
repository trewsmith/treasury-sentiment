# reddit_posts_raw.parquet — Data Dictionary

- **File:** `data/processed/reddit_posts_raw.parquet`
- **Rows:** 359,502 (submissions only; comments not collected)
- **With usable selftext:** 121,327 (rest are link/title-only, removed or deleted)
- **Created range:** 2025-01-01 00:00:37+00:00 → 2026-11-22 02:33:06+00:00

## Columns

| Column | Description |
|--------|-------------|
| post_id | Reddit base36 submission id (no `t3_` prefix); unique |
| subreddit | Subreddit name, lowercased |
| title | Post title |
| selftext | Post body for text posts; null for link posts. May be `[removed]` / `[deleted]` |
| author | Username; `[deleted]` when the account was deleted (kept, not filtered) |
| score | Net upvotes at `score_observed_at_utc` |
| upvote_ratio | Share of upvotes at observation time |
| num_comments | Comment count at observation time |
| created_utc | Post creation time (UTC, second precision) |
| permalink | Full https://www.reddit.com/… link to the post |
| url | Outbound link for link posts (equals permalink-style URL for text posts) |
| domain | Link domain (`self.<subreddit>` for text posts) |
| is_self | True for text posts |
| link_flair_text | Post flair (e.g. `Discussion`, `DD`, `Daily Discussion`) |
| over_18 | NSFW flag |
| stickied | Pinned by moderators (megathreads, rules posts) |
| distinguished | `moderator` / `admin` when posted in an official capacity |
| removed_by_category | Removal reason if removed (`moderator`, `automod_filtered`, `reddit`, `deleted`, …) |
| crosspost_parent | Fullname of the original post if this is a crosspost |
| ingest_method | `arctic_shift` (archive) or `praw` (official API) |
| score_observed_at_utc | When score / num_comments / removal were captured |
| collected_at_utc | When this pipeline collected the row |

## Counts by subreddit

- `r/wallstreetbets`: 202,340
- `r/stocks`: 75,840
- `r/investing`: 52,388
- `r/economics`: 24,550
- `r/bonds`: 3,674
- `r/securityanalysis`: 710

## Counts by ingest_method

- `arctic_shift`: 359,502

## Counts by removed_by_category

- `(not removed)`: 173,181
- `moderator`: 159,077
- `reddit`: 21,346
- `deleted`: 5,680
- `content_takedown`: 196
- `author`: 16
- `automod_filtered`: 6

## Notes

- **Source:** Arctic Shift archive (Pushshift successor) for history, chunked by subreddit-month and cached in `data/raw/reddit/arctic_shift/`. Optional PRAW top-up for the newest posts (`--with-praw`).
- **Scores are snapshots.** Archive rows carry the score from Arctic Shift's second retrieval, typically ~36h after posting (`score_observed_at_utc`); posts newer than that still show near-zero scores. PRAW rows are observed at collection time. Do not mix the two without accounting for this.
- **Raw = unfiltered.** Removed, deleted, stickied and NSFW posts are kept here; filtering happens in `src/cleaning/pipeline.py` → `documents_clean.parquet`.
- **Comments:** intentionally out of scope for the first pass.
