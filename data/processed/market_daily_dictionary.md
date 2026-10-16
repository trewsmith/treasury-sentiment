# market_daily.csv — Data Dictionary

- **Source:** FRED (Federal Reserve Economic Data) via FRED API
- **File:** `data/processed/market_daily.csv`
- **Date range requested:** 2000-01-01 to 2026-10-16
- **Rows:** 9,785
- **Join:** outer join on `date` (calendar days with any series observation)
- **Missing values:** FRED '.' observations stored as NaN

## Columns

| Column | FRED ID | Description | Units | Frequency | Role | Non-null |
|--------|---------|-------------|-------|-----------|------|----------|
| date | — | Observation date | YYYY-MM-DD | Daily | key | 9,785 |
| DGS10 | DGS10 | 10-Year Treasury Constant Maturity Rate | Percent | Daily | core_outcome | 6,699 |
| DGS2 | DGS2 | 2-Year Treasury Constant Maturity Rate | Percent | Daily | control | 6,699 |
| DFF | DFF | Effective Federal Funds Rate | Percent | Daily | control | 9,784 |
| VIXCLS | VIXCLS | CBOE Volatility Index (VIX) | Index | Daily | control | 6,771 |
| DTWEXBGS | DTWEXBGS | Trade Weighted U.S. Dollar Index: Broad, Goods and Services | Index (Jan 2006=100) | Daily | dollar_proxy | 5,208 |
| DEXUSEU | DEXUSEU | U.S. / Euro Foreign Exchange Rate | USD per EUR | Daily | dollar_proxy | 6,713 |
| BAMLH0A0HYM2 | BAMLH0A0HYM2 | ICE BofA US High Yield Index Option-Adjusted Spread | Percent | Daily | credit_risk | 786 |
| term_spread | — (DGS10 − DGS2) | 10y–2y Treasury term spread | Percentage points | Daily | derived | |

## Notes

- `DTWEXBGS` is the preferred broad dollar proxy (closest FRED stand-in for DXY).
- `DEXUSEU` is included as an additional FX series (USD per EUR).
- `BAMLH0A0HYM2` is the ICE BofA US High Yield OAS (credit risk / risk-off proxy).
- As of April 2026, FRED only distributes ~3 years of ICE BofA observations; longer history requires the ICE source directly.
- Series start dates differ; early rows may be sparse (e.g. `DTWEXBGS` begins ~2006).
- Set `FRED_API_KEY` in `.env` to use the official API (required for reliable pulls).
