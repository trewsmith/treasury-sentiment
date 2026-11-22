"""
Scheduled macro event calendar (FOMC, CPI, jobs report, ...).

Writes data/processed/events_calendar.parquet with one row per event:
  event_type, event_name, event_date, timestamp_et, timestamp_utc,
  is_scheduled, importance

FOMC dates are scraped from federalreserve.gov (current calendar + yearly
historical pages). Other releases come from the FRED release-dates endpoint,
which includes future scheduled dates. Release times are the usual time of day
from configs/events.yaml, not per-release timestamps.
"""

from __future__ import annotations

import re
from datetime import date

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup

from src.ingestion.fred_client import get_api_key
from src.utils.paths import (
    CONFIGS_DIR,
    EVENTS_CALENDAR_PARQUET,
    EVENTS_DICT_PATH,
    ensure_data_dirs,
)

FRED_RELEASE_DATES_URL = "https://api.stlouisfed.org/fred/release/dates"
FOMC_CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
FOMC_HISTORICAL_URL = "https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm"
HEADERS = {"User-Agent": "Mozilla/5.0 (treasury-sentiment research)"}

EVENT_COLUMNS = [
    "event_type",
    "event_name",
    "event_date",
    "timestamp_et",
    "timestamp_utc",
    "is_scheduled",
    "importance",
]

MONTHS = {
    m: i
    for i, m in enumerate(
        ["january", "february", "march", "april", "may", "june", "july",
         "august", "september", "october", "november", "december"],
        start=1,
    )
}
MONTH_ABBR = {k[:3]: v for k, v in MONTHS.items()}


def load_events_config() -> dict:
    with open(CONFIGS_DIR / "events.yaml") as f:
        return yaml.safe_load(f)


def _month_number(token: str) -> int | None:
    token = token.strip().lower().rstrip(".")
    return MONTHS.get(token) or MONTH_ABBR.get(token[:3])


def parse_meeting_label(label: str, year: int) -> tuple[date, bool] | None:
    """
    Parse a meeting label into (decision_date, is_scheduled).

    Handles "March 17-18*", "Apr/May 30-1", "July 31-August 1 Meeting - 2012",
    "March 15 (unscheduled) Meeting - 2020" and "May 9 Conference Call - 2010".
    The decision date is the last day of the meeting, which is when the
    statement comes out. Cancelled meetings and notation votes return None.
    """
    low = label.lower()
    if "cancel" in low or "notation vote" in low:
        return None
    is_scheduled = "conference call" not in low and "unscheduled" not in low
    text = re.sub(r"\(.*?\)", "", label)
    text = re.sub(r"\s*(Meeting|Conference Call).*$", "", text, flags=re.I).strip()
    text = text.replace("*", "").strip()

    # Meeting spans two months: "Apr/May 30-1" or "July 31-August 1".
    # The decision is in the second month.
    m = re.match(r"^([A-Za-z]+)/([A-Za-z]+)\s+(\d+)-(\d+)$", text)
    if m:
        month, day = _month_number(m.group(2)), int(m.group(4))
    else:
        m = re.match(r"^([A-Za-z]+)\s+(\d+)-([A-Za-z]+)\s+(\d+)$", text)
        if m:
            month, day = _month_number(m.group(3)), int(m.group(4))
        else:
            m = re.match(r"^([A-Za-z]+)\s+(\d+)(?:-(\d+))?$", text)
            if not m:
                return None
            month, day = _month_number(m.group(1)), int(m.group(3) or m.group(2))
    if not month:
        return None
    return date(year, month, day), is_scheduled


def _fetch_html(url: str) -> str | None:
    resp = requests.get(url, headers=HEADERS, timeout=60)
    if resp.status_code != 200:
        return None
    return resp.text


def _meetings_from_calendar(html: str) -> list[tuple[date, bool]]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for panel in soup.select(".panel.panel-default"):
        head = panel.select_one(".panel-heading")
        year_match = re.search(r"(\d{4})\s+FOMC", head.get_text(" ", strip=True)) if head else None
        if not year_match:
            continue
        year = int(year_match.group(1))
        for row in panel.select(".fomc-meeting"):
            month = row.select_one(".fomc-meeting__month")
            days = row.select_one(".fomc-meeting__date")
            if not (month and days):
                continue
            parsed = parse_meeting_label(
                f"{month.get_text(strip=True)} {days.get_text(strip=True)}", year
            )
            if parsed:
                out.append(parsed)
    return out


def _meetings_from_historical(html: str, year: int) -> list[tuple[date, bool]]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for panel in soup.select(".panel"):
        head = panel.select_one(".panel-heading")
        if not head:
            continue
        label = head.get_text(" ", strip=True)
        if not re.search(r"Meeting|Conference Call", label):
            continue
        parsed = parse_meeting_label(label, year)
        if parsed:
            out.append(parsed)
    return out


def fetch_fomc_dates(start_year: int, end_year: int | None = None) -> list[tuple[date, bool]]:
    """FOMC decision dates from start_year through the latest year on the Fed calendar."""
    end_year = end_year or date.today().year + 1
    found: dict[date, bool] = {}
    html = _fetch_html(FOMC_CALENDAR_URL)
    if html:
        for d, sched in _meetings_from_calendar(html):
            found[d] = sched
    for year in range(start_year, end_year + 1):
        if any(d.year == year for d in found):
            continue
        html = _fetch_html(FOMC_HISTORICAL_URL.format(year=year))
        if html:
            for d, sched in _meetings_from_historical(html, year):
                found[d] = sched
    return sorted((d, s) for d, s in found.items() if d.year >= start_year)


def fetch_fred_release_dates(release_id: int, start: str, api_key: str) -> list[date]:
    params = {
        "release_id": release_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": start,
        "realtime_end": "9999-12-31",
        "include_release_dates_with_no_data": "true",
        "limit": 10000,
        "sort_order": "asc",
    }
    resp = requests.get(FRED_RELEASE_DATES_URL, params=params, timeout=60)
    resp.raise_for_status()
    return [pd.Timestamp(r["date"]).date() for r in resp.json().get("release_dates", [])]


def _to_rows(
    dates: list[tuple[date, bool]],
    event_type: str,
    event_name: str,
    time_et: str,
    importance: int,
    time_et_pre_2013: str | None = None,
) -> list[dict]:
    rows = []
    for d, scheduled in dates:
        t = time_et_pre_2013 if (time_et_pre_2013 and d.year < 2013) else time_et
        rows.append(
            {
                "event_type": event_type,
                "event_name": event_name,
                "event_date": pd.Timestamp(d),
                "timestamp_et": pd.Timestamp(f"{d.isoformat()} {t}", tz="America/New_York"),
                "is_scheduled": scheduled,
                "importance": importance,
            }
        )
    return rows


def build_events_calendar(config: dict | None = None) -> pd.DataFrame:
    cfg = config or load_events_config()
    start_year = int(cfg.get("start_year", 2006))
    rows: list[dict] = []

    fomc = cfg["fomc"]
    rows += _to_rows(
        fetch_fomc_dates(start_year),
        "fomc",
        "FOMC decision",
        fomc["time_et"],
        fomc["importance"],
        fomc.get("time_et_pre_2013"),
    )

    api_key = get_api_key()
    if api_key:
        for etype, spec in cfg["fred_releases"].items():
            dates = fetch_fred_release_dates(spec["release_id"], f"{start_year}-01-01", api_key)
            rows += _to_rows(
                [(d, True) for d in dates], etype, spec["name"], spec["time_et"], spec["importance"]
            )
    else:
        print("FRED_API_KEY not set: only FOMC dates collected")

    df = pd.DataFrame(rows)
    df["timestamp_utc"] = df["timestamp_et"].dt.tz_convert("UTC")
    df = df.drop_duplicates(["event_type", "event_date"])
    df = df.sort_values(["timestamp_utc", "event_type"]).reset_index(drop=True)
    return df[EVENT_COLUMNS]


def write_dictionary(df: pd.DataFrame) -> None:
    counts = df.groupby("event_type").agg(
        n=("event_date", "size"), first=("event_date", "min"), last=("event_date", "max")
    )
    lines = [
        "# events_calendar.parquet — Data Dictionary",
        "",
        f"- **Rows:** {len(df):,}; built by `src/ingestion/events.py` from `configs/events.yaml`",
        "- **FOMC:** federalreserve.gov calendar + historical pages (decision day, statement time)",
        "- **Other releases:** FRED release dates (include future scheduled dates)",
        "- **Times** are the usual time of day for the release, not per-release timestamps",
        "",
        "## Columns",
        "",
        "| Column | Description |",
        "|---|---|",
        "| `event_type` | `fomc`, `cpi`, `nfp`, `pce`, `gdp`, `ppi`, `retail` |",
        "| `event_name` | Readable name |",
        "| `event_date` | Release date (ET calendar day) |",
        "| `timestamp_et` / `timestamp_utc` | Release time, tz-aware |",
        "| `is_scheduled` | False for unscheduled FOMC meetings and conference calls |",
        "| `importance` | 1–3, from config; for filtering event windows |",
        "",
        "## Coverage",
        "",
        "| event_type | events | first | last |",
        "|---|---|---|---|",
    ]
    for etype, r in counts.iterrows():
        lines.append(f"| {etype} | {r['n']} | {r['first']:%Y-%m-%d} | {r['last']:%Y-%m-%d} |")
    lines.append("")
    EVENTS_DICT_PATH.write_text("\n".join(lines))


def main() -> None:
    ensure_data_dirs()
    df = build_events_calendar()
    df.to_parquet(EVENTS_CALENDAR_PARQUET, index=False)
    write_dictionary(df)
    print(f"Wrote {EVENTS_CALENDAR_PARQUET} ({len(df):,} events)")
    print(df.groupby("event_type").size().to_string())


if __name__ == "__main__":
    main()
