# market_intraday.parquet — Data Dictionary

- **Rows:** 19,991 bars (5m), 2026-08-10 → 2026-11-20 (UTC)
- **Built by:** `src/ingestion/intraday.py` (`configs/intraday.yaml`)
- **Sources:** Yahoo Finance (~60-day window, accumulates on each run) and any vendor files in `data/raw/intraday/vendor/` (vendor wins on overlap)
- `timestamp_utc` is the bar start. Columns are NaN where a market was closed.
- Treasury futures prices move opposite to yields. `^TNX` is the 10y yield times 10.

| Column | Description | Non-null |
|---|---|---|
| `ust10_fut_close` | 10-Year T-Note futures (front month) (close) | 17,708 |
| `ust10_fut_volume` | 10-Year T-Note futures (front month) (volume) | 17,708 |
| `tnx_close` | CBOE 10-Year yield index (yield x10) (close) | 5,280 |
| `tnx_volume` | CBOE 10-Year yield index (yield x10) (volume) | 5,280 |
| `ust2_fut_close` | 2-Year T-Note futures (close) | 17,620 |
| `ust2_fut_volume` | 2-Year T-Note futures (volume) | 17,620 |
| `es_fut_close` | E-mini S&P 500 futures (close) | 17,707 |
| `es_fut_volume` | E-mini S&P 500 futures (volume) | 17,707 |
| `vix_close` | CBOE Volatility Index (close) | 11,646 |
| `vix_volume` | CBOE Volatility Index (volume) | 11,646 |
| `dxy_close` | US Dollar Index (DXY) (close) | 17,413 |
| `dxy_volume` | US Dollar Index (DXY) (volume) | 17,413 |
| `wti_fut_close` | WTI crude futures (close) | 17,755 |
| `wti_fut_volume` | WTI crude futures (volume) | 17,755 |
