# reddit_posts_raw.parquet — Data Dictionary

- **File:** `data/processed/reddit_posts_raw.parquet`
- **Rows:** 348,625 (submissions only; comments not collected)
- **With usable selftext:** 117,026 (rest are link/title-only, removed or deleted)
- **Created range:** 2025-01-01 00:00:37+00:00 → 2026-10-29 03:58:19+00:00

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

- `r/wallstreetbets`: 194,569
- `r/stocks`: 74,004
- `r/investing`: 51,750
- `r/economics`: 24,097
- `r/bonds`: 3,513
- `r/securityanalysis`: 692

## Counts by ingest_method

- `arctic_shift`: 348,625

## Counts by removed_by_category

- `(not removed)`: 165,819
- `moderator`: 156,271
- `reddit`: 20,650
- `deleted`: 5,680
- `content_takedown`: 184
- `author`: 16
- `automod_filtered`: 5

## Notes

- **Source:** Arctic Shift archive (Pushshift successor) for history, chunked by subreddit-month and cached in `data/raw/reddit/arctic_shift/`. Optional PRAW top-up for the newest posts (`--with-praw`).
- **Scores are snapshots.** Archive rows carry the score from Arctic Shift's second retrieval, typically ~36h after posting (`score_observed_at_utc`); posts newer than that still show near-zero scores. PRAW rows are observed at collection time. Do not mix the two without accounting for this.
- **Raw = unfiltered.** Removed, deleted, stickied and NSFW posts are kept here; filtering happens in `src/cleaning/pipeline.py` → `documents_clean.parquet`.
- **Comments:** intentionally out of scope for the first pass.
