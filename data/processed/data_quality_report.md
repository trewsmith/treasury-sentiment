# Data Quality Report — documents_clean.parquet

- **Generated:** 2026-10-29 04:04 UTC by `src/cleaning/pipeline.py`
- **Inputs:** `data/processed/news_raw.parquet`, `data/processed/reddit_posts_raw.parquet`
- **Output:** `data/processed/documents_clean.parquet`
- **Config:** `configs/cleaning.yaml`

## Summary

| source_type | raw rows | clean docs | kept |
|---|---|---|---|
| news | 8,459 | 8,208 | 97.0% |
| reddit | 348,625 | 150,087 | 43.1% |
| **total** | 357,084 | 158,295 | 44.3% |

## Cleaning funnel (rows dropped per step, in order)

| step | news dropped | reddit dropped | news remaining | reddit remaining |
|---|---|---|---|---|
| reddit: removed / deleted post | 0 | 182,806 | 8,459 | 165,819 |
| reddit: stickied (pinned) post | 0 | 324 | 8,459 | 165,495 |
| reddit: moderator/admin post | 0 | 109 | 8,459 | 165,386 |
| reddit: bot author | 0 | 1,232 | 8,459 | 164,154 |
| reddit: megathread / recurring thread | 0 | 881 | 8,459 | 163,273 |
| missing / unparseable timestamp | 112 | 0 | 8,347 | 163,273 |
| empty text | 0 | 9 | 8,347 | 163,264 |
| short text (news < 3, reddit < 5 words) | 107 | 9,999 | 8,240 | 153,265 |
| non-English | 1 | 166 | 8,239 | 153,099 |
| dedup: exact doc_id | 0 | 0 | 8,239 | 153,099 |
| dedup: same text within 24h (hash) | 31 | 3,012 | 8,208 | 150,087 |

Non-English drops by detected language: `de`: 73, `fr`: 31, `es`: 30, `non_latin`: 15, `pt`: 7, `it`: 6, `nl`: 5.

## Clean documents by source

| source_type | source_name | docs | with body | median words | first | last |
|---|---|---|---|---|---|---|
| news | federal_reserve | 6,135 | 1,800 | 15 | 2006-01-03 | 2026-10-16 |
| news | google_news | 1,756 | 3 | 12 | 2025-10-17 | 2026-10-16 |
| news | cnbc | 150 | 114 | 30 | 2026-09-18 | 2026-10-16 |
| news | marketwatch | 60 | 10 | 12 | 2024-02-27 | 2026-10-16 |
| news | seeking_alpha | 37 | 0 | 10 | 2026-10-16 | 2026-10-16 |
| news | investing | 36 | 0 | 10 | 2026-10-15 | 2026-10-16 |
| news | guardian | 34 | 34 | 118 | 2014-08-14 | 2026-10-16 |
| reddit | r/wallstreetbets | 83,670 | 61,865 | 24 | 2025-01-01 | 2026-10-29 |
| reddit | r/stocks | 22,211 | 22,193 | 125 | 2025-01-01 | 2026-10-29 |
| reddit | r/investing | 22,132 | 22,104 | 114 | 2025-01-01 | 2026-10-28 |
| reddit | r/economics | 18,395 | 0 | 12 | 2025-01-01 | 2026-10-29 |
| reddit | r/bonds | 3,151 | 2,676 | 64 | 2025-01-01 | 2026-10-28 |
| reddit | r/securityanalysis | 528 | 173 | 10 | 2025-01-01 | 2026-10-28 |

## Text length (words)

| source_type | p10 | median | p90 | p99 | share with body |
|---|---|---|---|---|---|
| news | 7 | 14 | 1677 | 5243 | 23.9% |
| reddit | 8 | 43 | 235 | 824 | 72.6% |

## Time coverage

- **news:** 2006-01-03 05:00 → 2026-10-16 20:35 UTC
- **reddit:** 2025-01-01 00:08 → 2026-10-29 03:48 UTC
- **Overlap (both sources present):** 2025-01-01 → 2026-10-16 — news 2,504 docs, reddit 148,540 docs

Documents per month (last 24 months, ET):

| month | news | reddit |
|---|---|---|
| 2024-11 | 25 | 0 |
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
| 2025-10 | 65 | 8,840 |
| 2025-11 | 50 | 5,626 |
| 2025-12 | 65 | 5,309 |
| 2026-01 | 65 | 6,622 |
| 2026-02 | 65 | 5,145 |
| 2026-03 | 85 | 5,148 |
| 2026-04 | 86 | 5,377 |
| 2026-05 | 106 | 6,697 |
| 2026-06 | 110 | 7,963 |
| 2026-07 | 173 | 4,738 |
| 2026-08 | 274 | 4,046 |
| 2026-09 | 595 | 3,695 |
| 2026-10 | 573 | 3,459 |

## Timestamp quality and alignment

- **Date-only timestamps:** 689 docs (news items stamped 00:00 ET with no time of day). Use them only for daily analysis; exclude from intraday windows.
- **yield_date null:** 2,109 docs (after the last available yield observation in market_daily.csv).

Market session (ET; `regular` = 09:30–16:00 weekdays, holidays not excluded):

| market_session | news | reddit |
|---|---|---|
| date_only | 689 | 0 |
| post | 959 | 40,929 |
| pre | 1,988 | 29,736 |
| regular | 4,405 | 53,768 |
| weekend | 167 | 25,654 |

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
- I Bonds could approach 5%. Should you wait until November to buy?
- US Posts $1.99 Trillion Budget Gap for 2026 on Spending Rise
- Old Navy returns to State Street in space slashed in half from 2023 lease
- US annual budget gap hits nearly $2 trillion, largest in 5 years
- The Government Killed Unlimited Grad School Loans. Will Tuition Finally Drop?
- Dark Matter Tech appoints new CFO in leadership shuffle
- The US federal budget deficit for 2026 just came in. It's $1.992 trillion.

**short text (news < 3, reddit < 5 words)**

- Risk retention
- Derivatives regulation
- Community banking
- Interchange fees
- Confirmation hearing
- Regulatory reform
- Bank supervision
- Regulatory restructuring

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

- Oil jump sends 30-year yields to two-decade high
- Wall Street rises as tech stocks climb and oil prices, bond yields hold relatively steady
- Auction result of Treasury Bonds - RIKB 38 0215 - RIKS 29 0917
- Global bond sell-off deepens, sending borrowing costs higher around the world
- Federal Reserve is expected to raise its benchmark rate, defying Trump’s demands
- Bond Market Sell-Off: Is It Really Safe to Invest Right Now?
- US Dollar Price Forecast: Treasury Yields Lift DXY as EUR/USD and GBP/USD Retreat
- Treasury Bond Auction Announcement - RIKB 29 0416 - RIKB 38 0215 - Switch Auction or Cash payment

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
