"""S&P 500 daily closes from Yahoo (2000-). FRED only distributes ~10 years, which cut the daily sample to 2016+.

Usage: PYTHONPATH=. python src/ingestion/sp500_history.py
Output: data/processed/sp500_history.csv (used by daily_regression.build_panel where FRED is missing)
"""
import time

import pandas as pd
import requests

from src.ingestion.intraday import HEADERS, YAHOO_CHART_URL, parse_yahoo_chart
from src.utils.paths import SP500_HISTORY_PATH


def main() -> None:
    r = requests.get(YAHOO_CHART_URL.format(symbol="^GSPC"), headers=HEADERS, timeout=60,
                     params=dict(interval="1d", period1=946684800, period2=int(time.time())))
    r.raise_for_status()
    b = parse_yahoo_chart(r.json())
    out = pd.DataFrame({"date": b.timestamp_utc.dt.tz_convert("America/New_York").dt.date, "sp500_yahoo": b.close}).dropna().drop_duplicates("date", keep="last")
    out.to_csv(SP500_HISTORY_PATH, index=False)
    print(f"wrote {SP500_HISTORY_PATH}: {len(out):,} days {out.date.min()} to {out.date.max()}")


if __name__ == "__main__":
    main()
