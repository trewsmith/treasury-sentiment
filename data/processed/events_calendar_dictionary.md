# events_calendar.parquet — Data Dictionary

- **Rows:** 1,794; built by `src/ingestion/events.py` from `configs/events.yaml`
- **FOMC:** federalreserve.gov calendar + historical pages (decision day, statement time)
- **Other releases:** FRED release dates (include future scheduled dates)
- **Times** are the usual time of day for the release, not per-release timestamps

## Columns

| Column | Description |
|---|---|
| `event_type` | `fomc`, `cpi`, `nfp`, `pce`, `gdp`, `ppi`, `retail` |
| `event_name` | Readable name |
| `event_date` | Release date (ET calendar day) |
| `timestamp_et` / `timestamp_utc` | Release time, tz-aware |
| `is_scheduled` | False for unscheduled FOMC meetings and conference calls |
| `importance` | 1–3, from config; for filtering event windows |

## Coverage

| event_type | events | first | last |
|---|---|---|---|
| cpi | 268 | 2006-01-18 | 2026-12-10 |
| fomc | 193 | 2006-01-31 | 2027-12-08 |
| gdp | 283 | 2006-01-27 | 2026-12-23 |
| nfp | 257 | 2006-01-06 | 2026-12-04 |
| pce | 257 | 2006-01-30 | 2026-12-23 |
| ppi | 268 | 2006-01-13 | 2026-12-15 |
| retail | 268 | 2006-01-13 | 2026-12-16 |
