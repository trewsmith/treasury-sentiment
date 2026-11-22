from datetime import date

import pandas as pd

from src.ingestion.events import parse_meeting_label
from src.ingestion.intraday import BAR_COLUMNS, build_wide, merge_bars, parse_yahoo_chart


def test_parse_meeting_label_variants():
    assert parse_meeting_label("March 17-18*", 2026) == (date(2026, 3, 18), True)
    assert parse_meeting_label("Apr/May 30-1", 2024) == (date(2024, 5, 1), True)
    assert parse_meeting_label("July 31-August 1  Meeting - 2012", 2012) == (date(2012, 8, 1), True)
    assert parse_meeting_label("March 15 (unscheduled) Meeting - 2020", 2020) == (date(2020, 3, 15), False)
    assert parse_meeting_label("May 9 Conference Call - 2010", 2010) == (date(2010, 5, 9), False)
    assert parse_meeting_label("March 17-18 (cancelled) Meeting - 2020", 2020) is None
    assert parse_meeting_label("March 19 (notation vote) - 2020", 2020) is None


def test_parse_yahoo_chart_drops_null_closes():
    payload = {"chart": {"result": [{
        "timestamp": [1700000000, 1700000300],
        "indicators": {"quote": [{"open": [1, 2], "high": [1, 2], "low": [1, 2],
                                  "close": [1.5, None], "volume": [10, 0]}]},
    }]}}
    df = parse_yahoo_chart(payload)
    assert list(df.columns) == BAR_COLUMNS and len(df) == 1
    assert parse_yahoo_chart({"chart": {"result": None}}).empty


def test_merge_bars_later_frame_wins_and_wide_aliases():
    ts = pd.to_datetime(["2026-01-02 14:30", "2026-01-02 14:35"], utc=True)
    a = pd.DataFrame({"timestamp_utc": ts, "open": 1, "high": 1, "low": 1, "close": [1.0, 2.0], "volume": 1})
    b = pd.DataFrame({"timestamp_utc": ts[1:], "open": 1, "high": 1, "low": 1, "close": [9.0], "volume": 5})
    merged = merge_bars(a, b)
    assert merged["close"].tolist() == [1.0, 9.0]
    wide = build_wide({"ust10_fut": merged})
    assert {"ust10_fut_close", "ust10_fut_volume"} <= set(wide.columns)
