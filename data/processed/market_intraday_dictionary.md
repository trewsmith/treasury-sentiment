# market_intraday.parquet — Data Dictionary

- **Rows:** 20,331 bars (5m), 2026-08-10 → 2026-11-24 (UTC)
- **Built by:** `src/ingestion/intraday.py` (`configs/intraday.yaml`)
- **Sources:** Yahoo Finance (~60-day window, accumulates on each run) and any vendor files in `data/raw/intraday/vendor/` (vendor wins on overlap)
- `timestamp_utc` is the bar start. Columns are NaN where a market was closed.
- Treasury futures prices move opposite to yields. `^TNX` is the 10y yield times 10.

| Column | Description | Non-null |
|---|---|---|
| `ust10_fut_close` | 10-Year T-Note futures (front month) (close) | 18,025 |
| `ust10_fut_volume` | 10-Year T-Note futures (front month) (volume) | 18,025 |
| `tnx_close` | CBOE 10-Year yield index (yield x10) (close) | 5,360 |
| `tnx_volume` | CBOE 10-Year yield index (yield x10) (volume) | 5,360 |
| `ust2_fut_close` | 2-Year T-Note futures (close) | 17,937 |
| `ust2_fut_volume` | 2-Year T-Note futures (volume) | 17,937 |
| `es_fut_close` | E-mini S&P 500 futures (close) | 18,024 |
| `es_fut_volume` | E-mini S&P 500 futures (volume) | 18,024 |
| `vix_close` | CBOE Volatility Index (close) | 11,803 |
| `vix_volume` | CBOE Volatility Index (volume) | 11,803 |
| `dxy_close` | US Dollar Index (DXY) (close) | 17,723 |
| `dxy_volume` | US Dollar Index (DXY) (volume) | 17,723 |
| `wti_fut_close` | WTI crude futures (close) | 18,072 |
| `wti_fut_volume` | WTI crude futures (volume) | 18,072 |
