"""
Intraday market bars for the 10-year Treasury and controls.

Sources, merged by timestamp (vendor wins on overlap):
  1. Yahoo Finance chart API (free, ~60 days of 5-minute bars, accumulates on each run)
  2. Vendor files in data/raw/intraday/vendor/<alias>.csv with columns
     timestamp (parseable, UTC if no tz), open, high, low, close, volume

Raw per-symbol bars live in data/raw/intraday/<alias>.parquet. The processed
file is a wide table: one row per bar start (UTC), `<alias>_close` and
`<alias>_volume` columns. Treasury futures prices move opposite to yields, so
returns are computed downstream, not here.
"""

from __future__ import annotations

import time

import pandas as pd
import requests
import yaml

from src.utils.paths import (
    CONFIGS_DIR,
    INTRADAY_RAW_DIR,
    MARKET_HOURLY_PARQUET,
    MARKET_INTRADAY_DICT_PATH,
    MARKET_INTRADAY_PARQUET,
    ensure_data_dirs,
)

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-client)"}
BAR_COLUMNS = ["timestamp_utc", "open", "high", "low", "close", "volume"]
VENDOR_DIR = INTRADAY_RAW_DIR / "vendor"


def load_intraday_config() -> dict:
    with open(CONFIGS_DIR / "intraday.yaml") as f:
        return yaml.safe_load(f)


def parse_yahoo_chart(payload: dict) -> pd.DataFrame:
    """Turn a Yahoo chart JSON payload into a bar frame (empty if no data)."""
    result = (payload.get("chart") or {}).get("result") or []
    if not result or not result[0].get("timestamp"):
        return pd.DataFrame(columns=BAR_COLUMNS)
    r = result[0]
    quote = r["indicators"]["quote"][0]
    df = pd.DataFrame(
        {
            "timestamp_utc": pd.to_datetime(r["timestamp"], unit="s", utc=True),
            "open": quote.get("open"),
            "high": quote.get("high"),
            "low": quote.get("low"),
            "close": quote.get("close"),
            "volume": quote.get("volume"),
        }
    )
    return df.dropna(subset=["close"]).reset_index(drop=True)


def fetch_yahoo_bars(symbol: str, interval: str = "5m", range_: str = "60d") -> pd.DataFrame:
    resp = requests.get(
        YAHOO_CHART_URL.format(symbol=symbol),
        params={"interval": interval, "range": range_, "includePrePost": "true"},
        headers=HEADERS,
        timeout=60,
    )
    resp.raise_for_status()
    return parse_yahoo_chart(resp.json())


def read_vendor_bars(alias: str, vendor_dir=VENDOR_DIR) -> pd.DataFrame:
    """Load a vendor CSV for this alias, normalized to BAR_COLUMNS in UTC."""
    path = vendor_dir / f"{alias}.csv"
    if not path.exists():
        return pd.DataFrame(columns=BAR_COLUMNS)
    df = pd.read_csv(path)
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    ts_col = next((c for c in ("timestamp", "ts_event", "datetime", "time", "date") if c in df), None)
    if ts_col is None:
        raise ValueError(f"{path}: no timestamp column (expected timestamp/ts_event/datetime)")
    out = pd.DataFrame({"timestamp_utc": pd.to_datetime(df[ts_col], utc=True)})
    for col in ("open", "high", "low", "close", "volume"):
        out[col] = df[col] if col in df else pd.NA
    return out.dropna(subset=["close"]).reset_index(drop=True)


def merge_bars(*frames: pd.DataFrame) -> pd.DataFrame:
    """Concat bar frames; on duplicate timestamps the later frame wins."""
    frames = [f for f in frames if len(f)]
    if not frames:
        return pd.DataFrame(columns=BAR_COLUMNS)
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates("timestamp_utc", keep="last")
    return df.sort_values("timestamp_utc").reset_index(drop=True)[BAR_COLUMNS]


def update_symbol(alias: str, spec: dict, interval: str, range_: str, fetch=fetch_yahoo_bars, suffix: str = "") -> pd.DataFrame:
    """Fetch new bars for one symbol, merge into its raw parquet, return the merged frame."""
    INTRADAY_RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = INTRADAY_RAW_DIR / f"{alias}{suffix}.parquet"
    old = pd.read_parquet(path) if path.exists() else pd.DataFrame(columns=BAR_COLUMNS)
    try:
        new = fetch(spec["yahoo"], interval, range_)
    except requests.RequestException as exc:
        print(f"  {alias}: Yahoo fetch failed ({exc}); keeping existing bars")
        new = pd.DataFrame(columns=BAR_COLUMNS)
    merged = merge_bars(old, new, read_vendor_bars(alias + suffix))
    if len(merged):
        merged.to_parquet(path, index=False)
    return merged


def build_wide(bars: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Wide table indexed by bar start: `<alias>_close` and `<alias>_volume`."""
    parts = []
    for alias, df in bars.items():
        if df.empty:
            continue
        part = df.set_index("timestamp_utc")[["close", "volume"]]
        part.columns = [f"{alias}_close", f"{alias}_volume"]
        parts.append(part)
    if not parts:
        return pd.DataFrame()
    wide = pd.concat(parts, axis=1, sort=True)
    wide.index.name = "timestamp_utc"
    return wide.reset_index()


def write_dictionary(cfg: dict, wide: pd.DataFrame) -> None:
    lines = [
        "# market_intraday.parquet — Data Dictionary",
        "",
        f"- **Rows:** {len(wide):,} bars ({cfg['interval']}), "
        f"{wide['timestamp_utc'].min():%Y-%m-%d} → {wide['timestamp_utc'].max():%Y-%m-%d} (UTC)",
        "- **Built by:** `src/ingestion/intraday.py` (`configs/intraday.yaml`)",
        "- **Sources:** Yahoo Finance (~60-day window, accumulates on each run) and any vendor "
        "files in `data/raw/intraday/vendor/` (vendor wins on overlap)",
        "- `timestamp_utc` is the bar start. Columns are NaN where a market was closed.",
        "- Treasury futures prices move opposite to yields. `^TNX` is the 10y yield times 10.",
        "",
        "| Column | Description | Non-null |",
        "|---|---|---|",
    ]
    for alias, spec in cfg["symbols"].items():
        for kind in ("close", "volume"):
            col = f"{alias}_{kind}"
            if col in wide:
                lines.append(f"| `{col}` | {spec['name']} ({kind}) | {int(wide[col].notna().sum()):,} |")
    lines.append("")
    MARKET_INTRADAY_DICT_PATH.write_text("\n".join(lines))


def main() -> None:
    ensure_data_dirs()
    cfg = load_intraday_config()
    bars = {}
    for alias, spec in cfg["symbols"].items():
        merged = update_symbol(alias, spec, cfg["interval"], cfg["yahoo_range"])
        bars[alias] = merged
        span = f"{merged['timestamp_utc'].min():%Y-%m-%d} → {merged['timestamp_utc'].max():%Y-%m-%d}" if len(merged) else "no data"
        print(f"  {alias:10s} {len(merged):>7,} bars  {span}")
        time.sleep(0.5)
    wide = build_wide(bars)
    if wide.empty:
        print("No intraday data collected")
        return
    wide.to_parquet(MARKET_INTRADAY_PARQUET, index=False)
    write_dictionary(cfg, wide)
    print(f"Wrote {MARKET_INTRADAY_PARQUET} ({len(wide):,} bars)")

    if cfg.get("hourly"):
        h = cfg["hourly"]
        hbars = {}
        for alias, spec in cfg["symbols"].items():
            b = update_symbol(alias, spec, h["interval"], h["yahoo_range"], suffix="_60m")
            ts = pd.to_datetime(b["timestamp_utc"], utc=True)
            hbars[alias] = b[(ts.dt.minute == 0) & (ts.dt.second == 0)]  # drop the live partial tick
            print(f"  {alias + '_60m':14s} {len(hbars[alias]):>7,} bars on the hour of {len(b):,}")
            time.sleep(0.5)
        hw = build_wide(hbars)
        hw.to_parquet(MARKET_HOURLY_PARQUET, index=False)
        print(f"Wrote {MARKET_HOURLY_PARQUET} ({len(hw):,} bars)")


if __name__ == "__main__":
    main()
