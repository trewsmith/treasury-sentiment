"""
FRED ingestion client for daily market series.

Requires a free API key (recommended):
  https://fred.stlouisfed.org/docs/api/api_key.html

Set FRED_API_KEY in the environment or a project-root .env file.
If no key is set, falls back to the public fredgraph.csv endpoint.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

from src.utils.paths import (
    CONFIGS_DIR,
    FRED_RAW_DIR,
    MARKET_DAILY_PATH,
    MARKET_DICT_PATH,
    PROJECT_ROOT,
    ensure_data_dirs,
)

FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_GRAPH_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
DEFAULT_START = "2000-01-01"


def _load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def get_api_key() -> str | None:
    """Return FRED_API_KEY if present."""
    _load_env()
    key = os.getenv("FRED_API_KEY", "").strip()
    if not key or key.startswith("your_"):
        return None
    return key


def load_fred_config(config_path: Path | None = None) -> dict:
    """Load series metadata and default date window from configs/fred.yaml."""
    path = config_path or (CONFIGS_DIR / "fred.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def default_series_ids(config: dict | None = None) -> list[str]:
    cfg = config or load_fred_config()
    return list(cfg["series"].keys())


def _parse_observations(payload: dict, series_id: str) -> pd.DataFrame:
    rows = payload.get("observations", [])
    if not rows:
        return pd.DataFrame(columns=["date", series_id])

    df = pd.DataFrame(rows)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.rename(columns={"value": series_id})


def _fetch_via_api(
    series_id: str,
    start: str,
    end: str,
    api_key: str,
) -> pd.DataFrame:
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "observation_end": end,
        "sort_order": "asc",
    }
    resp = requests.get(FRED_API_URL, params=params, timeout=60)
    resp.raise_for_status()
    return _parse_observations(resp.json(), series_id)


def _fetch_via_graph_csv(series_id: str, start: str, end: str) -> pd.DataFrame:
    """Public CSV fallback when no API key is configured."""
    params = {"id": series_id, "cosd": start, "coed": end}
    resp = requests.get(FRED_GRAPH_CSV_URL, params=params, timeout=60)
    resp.raise_for_status()

    from io import StringIO

    df = pd.read_csv(StringIO(resp.text))
    if df.empty:
        return pd.DataFrame(columns=["date", series_id])

    date_col = df.columns[0]
    value_col = df.columns[1]
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_col]),
            series_id: pd.to_numeric(df[value_col], errors="coerce"),
        }
    )
    return out.sort_values("date").reset_index(drop=True)


def fetch_series(
    series_id: str,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """
    Fetch one FRED series as a two-column DataFrame: date, <series_id>.

    Missing FRED values ('.') become NaN.
    """
    cfg = load_fred_config()
    start = start or cfg.get("start_date") or DEFAULT_START
    end = end or cfg.get("end_date") or date.today().isoformat()

    api_key = get_api_key()
    if api_key:
        return _fetch_via_api(series_id, start, end, api_key)
    return _fetch_via_graph_csv(series_id, start, end)


def save_raw_series(
    series_id: str,
    start: str | None = None,
    end: str | None = None,
    out_dir: Path | None = None,
) -> Path:
    """Fetch a series and write data/raw/fred/<series_id>.csv. Returns path."""
    ensure_data_dirs()
    df = fetch_series(series_id, start=start, end=end)
    target_dir = out_dir or FRED_RAW_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{series_id}.csv"
    df.to_csv(path, index=False)
    return path


def merge_market_series(
    series_ids: Iterable[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    save: bool = True,
) -> pd.DataFrame:
    """
    Pull configured FRED series, outer-join on date, optionally save deliverables.

    Adds term_spread = DGS10 - DGS2 when both columns are present.
    Writes:
      - data/processed/market_daily.csv
      - data/processed/market_daily_dictionary.md
    """
    ensure_data_dirs()
    cfg = load_fred_config()
    start = start or cfg.get("start_date") or DEFAULT_START
    end = end or cfg.get("end_date") or date.today().isoformat()
    ids = list(series_ids) if series_ids is not None else default_series_ids(cfg)

    frames: list[pd.DataFrame] = []
    for series_id in ids:
        raw_path = save_raw_series(series_id, start=start, end=end)
        frames.append(pd.read_csv(raw_path, parse_dates=["date"]))

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="date", how="outer")

    merged = merged.sort_values("date").reset_index(drop=True)

    if {"DGS10", "DGS2"}.issubset(merged.columns):
        merged["term_spread"] = (merged["DGS10"] - merged["DGS2"]).round(4)

    if save:
        merged.to_csv(MARKET_DAILY_PATH, index=False)
        write_data_dictionary(
            cfg,
            ids,
            start=start,
            end=end,
            n_rows=len(merged),
            used_api=get_api_key() is not None,
            coverage=merged[ids].notna().sum().to_dict() if ids else {},
        )

    return merged


def write_data_dictionary(
    config: dict,
    series_ids: list[str],
    start: str,
    end: str,
    n_rows: int,
    used_api: bool = False,
    coverage: dict | None = None,
) -> Path:
    """Write a markdown data dictionary for market_daily.csv."""
    source_mode = "FRED API" if used_api else "fredgraph.csv (public fallback)"
    lines = [
        "# market_daily.csv — Data Dictionary",
        "",
        f"- **Source:** FRED (Federal Reserve Economic Data) via {source_mode}",
        f"- **File:** `data/processed/market_daily.csv`",
        f"- **Date range requested:** {start} to {end}",
        f"- **Rows:** {n_rows:,}",
        f"- **Join:** outer join on `date` (calendar days with any series observation)",
        f"- **Missing values:** FRED '.' observations stored as NaN",
        "",
        "## Columns",
        "",
        "| Column | FRED ID | Description | Units | Frequency | Role | Non-null |",
        "|--------|---------|-------------|-------|-----------|------|----------|",
        f"| date | — | Observation date | YYYY-MM-DD | Daily | key | {n_rows:,} |",
    ]

    meta = config.get("series", {})
    coverage = coverage or {}
    for series_id in series_ids:
        info = meta.get(series_id, {})
        n_obs = coverage.get(series_id, "")
        n_obs_str = f"{int(n_obs):,}" if n_obs != "" else ""
        lines.append(
            "| {col} | {sid} | {name} | {units} | {freq} | {role} | {n} |".format(
                col=series_id,
                sid=series_id,
                name=info.get("name", series_id),
                units=info.get("units", ""),
                freq=info.get("frequency", "Daily"),
                role=info.get("role", ""),
                n=n_obs_str,
            )
        )

    if "DGS10" in series_ids and "DGS2" in series_ids:
        lines.append(
            "| term_spread | — (DGS10 − DGS2) | 10y–2y Treasury term spread | "
            "Percentage points | Daily | derived | |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `DTWEXBGS` is the preferred broad dollar proxy (closest FRED stand-in for DXY).",
            "- `DEXUSEU` is included as an additional FX series (USD per EUR).",
            "- `BAMLH0A0HYM2` is the ICE BofA US High Yield OAS (credit risk / risk-off proxy).",
            "- As of April 2026, FRED only distributes ~3 years of ICE BofA observations; "
            "longer history requires the ICE source directly.",
            "- Series start dates differ; early rows may be sparse (e.g. `DTWEXBGS` begins ~2006).",
            "- Set `FRED_API_KEY` in `.env` to use the official API (required for reliable pulls).",
            "",
        ]
    )

    MARKET_DICT_PATH.write_text("\n".join(lines))
    return MARKET_DICT_PATH


def main() -> None:
    """Pull all configured series and write deliverables."""
    api_key = get_api_key()
    mode = "FRED API" if api_key else "fredgraph.csv fallback (set FRED_API_KEY for official API)"
    print(f"Pulling market series via {mode}")

    df = merge_market_series(save=True)
    print(f"Wrote {MARKET_DAILY_PATH} ({len(df):,} rows, {len(df.columns)} columns)")
    print(f"Wrote {MARKET_DICT_PATH}")
    print(df.tail())


if __name__ == "__main__":
    main()
