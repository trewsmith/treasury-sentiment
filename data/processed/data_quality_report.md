# Data Quality Report — documents_clean.parquet

- **Generated:** 2026-11-24 00:55 UTC by `src/cleaning/pipeline.py`
- **Inputs:** `data/processed/news_raw.parquet`, `data/processed/reddit_posts_raw.parquet`
- **Output:** `data/processed/documents_clean.parquet`
- **Config:** `configs/cleaning.yaml`

## Summary

| source_type | raw rows | clean docs | kept |
|---|---|---|---|
| news | 8,105 | 7,874 | 97.1% |
| reddit | 360,880 | 156,973 | 43.5% |
| **total** | 368,985 | 164,847 | 44.7% |

## Cleaning funnel (rows dropped per step, in order)

| step | news dropped | reddit dropped | news remaining | reddit remaining |
|---|---|---|---|---|
| reddit: removed / deleted post | 0 | 186,703 | 8,105 | 174,177 |
| reddit: stickied (pinned) post | 0 | 328 | 8,105 | 173,849 |
| reddit: moderator/admin post | 0 | 131 | 8,105 | 173,718 |
| reddit: bot author | 0 | 1,284 | 8,105 | 172,434 |
| reddit: megathread / recurring thread | 0 | 901 | 8,105 | 171,533 |
| missing / unparseable timestamp | 92 | 0 | 8,013 | 171,533 |
| empty text | 0 | 9 | 8,013 | 171,524 |
| short text (news < 3, reddit < 5 words) | 112 | 11,224 | 7,901 | 160,300 |
| non-English | 1 | 178 | 7,900 | 160,122 |
| dedup: exact doc_id | 0 | 0 | 7,900 | 160,122 |
| dedup: same text within 24h (hash) | 26 | 3,149 | 7,874 | 156,973 |

Non-English drops by detected language: `de`: 76, `es`: 31, `fr`: 31, `non_latin`: 16, `it`: 13, `pt`: 7, `nl`: 5.

## Clean documents by source

| source_type | source_name | docs | with body | median words | first | last |
|---|---|---|---|---|---|---|
| news | federal_reserve | 6,155 | 1,800 | 15 | 2006-01-03 | 2026-11-20 |
| news | google_news | 1,441 | 2 | 11 | 2025-11-24 | 2026-11-24 |
| news | cnbc | 147 | 113 | 31 | 2026-10-26 | 2026-11-24 |
| news | marketwatch | 58 | 10 | 12 | 2024-02-27 | 2026-11-24 |
| news | seeking_alpha | 37 | 0 | 10 | 2026-11-23 | 2026-11-24 |
| news | investing | 36 | 0 | 10 | 2026-11-23 | 2026-11-24 |
| reddit | r/wallstreetbets | 88,958 | 65,135 | 23 | 2025-01-01 | 2026-11-24 |
| reddit | r/stocks | 22,893 | 22,874 | 126 | 2025-01-01 | 2026-11-23 |
| reddit | r/investing | 22,510 | 22,479 | 114 | 2025-01-01 | 2026-11-23 |
| reddit | r/economics | 18,805 | 0 | 12 | 2025-01-01 | 2026-11-23 |
| reddit | r/bonds | 3,263 | 2,776 | 64 | 2025-01-01 | 2026-11-23 |
| reddit | r/securityanalysis | 544 | 178 | 10 | 2025-01-01 | 2026-11-22 |

## Text length (words)

| source_type | p10 | median | p90 | p99 | share with body |
|---|---|---|---|---|---|
| news | 7 | 14 | 1801 | 5297 | 24.4% |
| reddit | 8 | 41 | 234 | 821 | 72.3% |

## Time coverage

- **news:** 2006-01-03 05:00 → 2026-11-24 00:32 UTC
- **reddit:** 2025-01-01 00:08 → 2026-11-24 00:49 UTC
- **Overlap (both sources present):** 2025-01-01 → 2026-11-24 — news 2,174 docs, reddit 156,969 docs

Documents per month (last 24 months, ET):

| month | news | reddit |
|---|---|---|
| 2024-12 | 20 | 57 |
| 2025-01 | 15 | 8,793 |
| 2025-02 | 28 | 8,176 |
| 2025-03 | 17 | 7,694 |
| 2025-04 | 23 | 12,945 |
| 2025-05 | 22 | 9,288 |
| 2025-06 | 32 | 7,252 |
| 2025-07 | 19 | 9,333 |
| 2025-08 | 17 | 7,090 |
| 2025-09 | 19 | 6,794 |
| 2025-10 | 31 | 8,840 |
| 2025-11 | 31 | 5,626 |
| 2025-12 | 74 | 5,309 |
| 2026-01 | 65 | 6,622 |
| 2026-02 | 48 | 5,145 |
| 2026-03 | 86 | 5,148 |
| 2026-04 | 55 | 5,377 |
| 2026-05 | 88 | 6,697 |
| 2026-06 | 69 | 7,963 |
| 2026-07 | 120 | 4,738 |
| 2026-08 | 154 | 4,046 |
| 2026-09 | 413 | 3,695 |
| 2026-10 | 292 | 4,116 |
| 2026-11 | 456 | 6,229 |

## Timestamp quality and alignment

- **Date-only timestamps:** 690 docs (news items stamped 00:00 ET with no time of day). Use them only for daily analysis; exclude from intraday windows.
- **yield_date null:** 1,446 docs (after the last available yield observation in market_daily.csv).

Market session (ET; `regular` = 09:30–16:00 weekdays, holidays not excluded):

| market_session | news | reddit |
|---|---|---|
| date_only | 690 | 0 |
| post | 1,007 | 42,900 |
| pre | 1,685 | 31,105 |
| regular | 4,309 | 56,158 |
| weekend | 183 | 26,810 |

## Examples of dropped rows (for auditing filters)

**reddit: removed / deleted post**

- I had my options ark this year
- First Time Stock Buyer
- Backtested VOO and HFEA variants with ER and accurate LETF Simulation
- Can someone explain?
- SMCI isn’t the only thing that’s super micro
- Marathon digital
- [Beginner] New to Stock Investing – Seeking Advice on Good Stocks for a 3–5 Year Time Horizon
- A failed $7k YOLO.  Down but not out.  💎🙌🏽

**reddit: stickied (pinned) post**

- Weekly Earnings Thread 1/6 - 1/10
- Weekend Discussion Thread for the Weekend of January 03, 2025
- /r/Stocks Weekend Discussion Saturday - Jan 04, 2025
- Q4 2024 Letters & Reports
- Weekly Earnings Thread 1/13 - 1/17
- Weekend Discussion Thread for the Weekend of January 10, 2025
- /r/Stocks Weekend Discussion Saturday - Jan 11, 2025
- 2025 Analysis Questions and Discussions Thread

**reddit: moderator/admin post**

- Reminder: No Politics on WSB
- Moderator's Update on Paper Trading Competition
- If you got a DM it is a scam! Reddit is stupid enough to have let someone reddit request "waListreetbets" and they are s
- This is a test of the new scoreboard system
- everyone take money out of ur bank tomorrow we gon start a run on the banks
- What Are Your Moves Tomorrow, June 18, 2026
- What Are Your Moves for Juneteenth, June 19, 2026
- What Are Your Moves Tomorrow, June 22, 2026

**reddit: bot author**

- Daily General Discussion and Advice Thread - January 01, 2025
- r/Stocks Daily Discussion Wednesday - Jan 01, 2025
- Daily General Discussion and Advice Thread - January 02, 2025
- r/Stocks Daily Discussion & Options Trading Thursday - Jan 02, 2025
- Daily General Discussion and Advice Thread - January 03, 2025
- r/Stocks Daily Discussion & Fundamentals Friday Jan 03, 2025
- Daily General Discussion and Advice Thread - January 04, 2025
- r/Stocks Weekly Thread on Meme Stocks Saturday - Jan 04, 2025

**reddit: megathread / recurring thread**

- Daily Discussion Thread for January 01, 2025
- What Are Your Moves Tomorrow, January 02, 2025
- Daily Discussion Thread for January 02, 2025
- What Are Your Moves Tomorrow, January 03, 2025
- Daily Discussion Thread for January 03, 2025
- What Are Your Moves Tomorrow, January 06, 2025
- Daily Discussion Thread for January 06, 2025
- What Are Your Moves Tomorrow, January 07, 2025

**missing / unparseable timestamp**

- 
- Trump signs Common Cents Act, setting rules for post-penny era
- Zoom Projects Revenue That Misses Estimates on Stagnant Growth
- GE Aerospace defense unit chief Amy Gowder to step down
- Trump Slams Newsom for Commuting Death Sentences in 2028 Preview
- Cambridge Savings adds a digital stalwart to its board
- Earnest student loan review: Flexible repayment with no fees
- Jensen Huang returns to Nvidia headquarters to cheering employees

**short text (news < 3, reddit < 5 words)**

- Economic Outlook
- Fed Watch
- Banking supervision
- Risk retention
- Derivatives regulation
- Community banking
- Interchange fees
- Confirmation hearing

**non-English**

- La Ayuda al consumidor de la Reserva Federal actualmente ofrece una versión de su página web en español
- mach mich reich..
- Trade Scheispuplic
- Calls oder Puts morgen auf TESLA APPLE AMAZON META?
- Binance futures/hebel gamble action
- Realbotix 20% im Plus aber alle interessieren sich nur für ewiggestrige Hans Wurst Aktien wie Nvidia.
- Jp Morgan 💩
- Offizielle Anfrage Hildegard (98) in diesen Subreddit aufzunehmen

**dedup: same text within 24h (hash)**

- Fed holds rates steady despite concerns over inflation
- Wall Street rises as tech stocks climb and oil prices, bond yields hold relatively steady
- Trillion-Dollar Dislocation Hides in Calm Credit Markets
- Here are five key takeaways from the Fed rate decision and Warsh news conference
- Bond selloff deepens as oil prices and public debt fears jolt markets
- Tech stocks lead a rally on Wall Street as bond yields ease some more
- Why bond yields are rising and why everyone should care
- Federal Reserve rate hike reflects new world of sticky inflation and faster growth

## Cleaning rules

1. **Reddit platform filters** (raw posts): drop `removed_by_category` in `moderator`, `automod_filtered`, `reddit`, `deleted`, `author`, `anti_evil_ops`, `copyright_takedown`, `content_takedown`, `community_ops`; stickied posts; moderator/admin-distinguished posts; bot authors (AutoModerator, VisualMod, QualityVote); titles matching megathread patterns. Posts by deleted accounts are kept when the post text itself survives.
2. **Text normalization:** HTML → text, entity unescaping, Unicode NFKC, zero-width characters removed, URLs removed, Reddit markdown stripped, boilerplate lines removed (e.g. *For media inquiries…*, *For release at…*, *Continue reading…*, bare datelines), whitespace collapsed. Google News titles have the ` - Publisher` suffix moved to `meta.publisher`. Bodies that only repeat the headline are dropped (`body` = null).
3. **Timezone:** all timestamps parsed as UTC (`timestamp_utc`), converted to America/New_York for `timestamp_et` / `et_date` / `market_session`.
4. **Missing timestamp:** dropped (cannot be aligned to market data; collection time is not used as a substitute because it is not the publication time).
5. **Empty / short:** dropped when `text` has fewer than 3 words (news), 5 words (reddit).
6. **Language:** English only (script check + stopword-ratio heuristic, `src/cleaning/language.py`).
7. **Dedup:** exact `doc_id`, then identical normalized text (`text_hash`) within the same source_type reappearing within 24h of the previous copy; the earliest copy is kept.

## Column dictionary

| Column | Description |
|--------|-------------|
| doc_id | `news:<article_id>` or `reddit:<post_id>`; unique |
| source_type | `news` or `reddit` |
| source_name | Publisher label (`cnbc`, `federal_reserve`, `google_news`, …) or `r/<subreddit>` |
| timestamp_utc | Publication / post time, UTC |
| headline | Cleaned headline / post title |
| body | Cleaned body / selftext; null when absent or redundant with headline |
| text | `headline` + blank line + `body` — the field to feed NLP models |
| meta | JSON string of source fields (news: article_id, url, section, tag, ingest_method, publisher, collected_at_utc; reddit: post_id, subreddit, author, score, upvote_ratio, num_comments, permalink, url, domain, is_self, link_flair_text, over_18, crosspost_parent, ingest_method, score_observed_at_utc). Flatten with `src.cleaning.documents.expand_meta`. |
| timestamp_et | `timestamp_utc` in America/New_York |
| et_date | Calendar date in ET (naive, midnight) — joins to `market_daily.csv` `date` |
| market_session | `pre` / `regular` / `post` / `weekend` (ET), or `date_only` |
| yield_date | First `DGS10` observation date that can reflect the doc: same ET date if before 15:30 ET (CMT yields are fixed from ~3:30 p.m. bid quotes), else the next date with an observation (skips weekends and holidays). Join on `market_daily.csv` `date` for daily regressions |
| timestamp_is_date_only | True when the source only provided a date (00:00 ET) |
| n_words | Whitespace token count of `text` |
| text_hash | SHA-256 (32 hex) of normalized `text`; used for dedup |

## Known limitations

- Reddit `score` / `num_comments` are archive snapshots taken shortly after posting (`meta.score_observed_at_utc`) and understate final engagement.
- Language detection is heuristic; very short ticker-heavy posts default to English.
- `market_session` ignores exchange holidays and early closes; `yield_date` handles holidays via the actual yield observation calendar.
- News coverage is uneven over time (Fed archive is multi-year; RSS / Google News are recent), so compare news vs. Reddit inside the overlap window.
