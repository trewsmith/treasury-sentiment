"""Event study: do scheduled macro releases move the 10y more than ordinary days at the same time?

Unit = unique release time (simultaneous releases count once). For release time T and horizon h in
{5, 30, 60} min, move = |10y futures log return| (bp of price) from T to T+h; price at T = close of the
bar that starts T-5min. Baseline = the same ET clock time (DST-safe) on weekdays with no calendar event,
each (day, clock time) used once. Permutation shuffles event labels across days WITHIN clock-time slot,
so the test is stratified by time of day and no observation is duplicated.

Usage: PYTHONPATH=. python src/modeling/event_study.py [--min-importance 2]
Output: reports/tables/event_study.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from src.utils.paths import PROCESSED_DIR, PROJECT_ROOT

HORIZONS = (5, 30, 60)
ET = "America/New_York"


def price_at(close: pd.Series, t: pd.Timestamp):
    """Price at time t = close of the bar that starts 5 min earlier."""
    return close.get(t - pd.Timedelta(minutes=5), np.nan)


def abs_move(close: pd.Series, t: pd.Timestamp, h: int) -> float:
    p0, p1 = price_at(close, t), price_at(close, t + pd.Timedelta(minutes=h))
    return abs(np.log(p1 / p0)) * 1e4 if np.isfinite(p0) and np.isfinite(p1) else np.nan


def build_sample(close: pd.Series, times: pd.DatetimeIndex, all_event_days: set, h: int) -> pd.DataFrame:
    """One row per unique (day, clock slot): move, slot, is_event."""
    rows = []
    et = times.tz_convert(ET)
    days = pd.bdate_range(close.index.min().tz_convert(ET).date(), close.index.max().tz_convert(ET).date())
    for t in et.unique():
        rows.append((t.strftime("%H:%M"), True, abs_move(close, t.tz_convert("UTC"), h)))
    for slot in sorted(set(et.strftime("%H:%M"))):
        for d in days:
            if d.date() in all_event_days:
                continue
            t = pd.Timestamp(f"{d:%Y-%m-%d} {slot}").tz_localize(ET)
            rows.append((slot, False, abs_move(close, t.tz_convert("UTC"), h)))
    return pd.DataFrame(rows, columns=["slot", "is_event", "move"]).dropna()


def stat(s: pd.DataFrame, lab: np.ndarray) -> float:
    """Event mean minus slot-matched baseline mean (slots weighted by number of events)."""
    tot, n = 0.0, 0
    mv = s.move.to_numpy()
    for idx in s.groupby("slot").indices.values():
        e = lab[idx]
        if e.any() and (~e).any():
            tot += e.sum() * (mv[idx][e].mean() - mv[idx][~e].mean())
            n += e.sum()
    return tot / n if n else np.nan


def perm_p(s: pd.DataFrame, n=10000, seed=0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    lab = s.is_event.to_numpy()
    obs = stat(s, lab)
    groups = list(s.groupby("slot").indices.values())
    cnt = 0
    for _ in range(n):
        p = lab.copy()
        for g in groups:
            p[g] = rng.permutation(p[g])
        cnt += stat(s, p) >= obs
    return obs, (cnt + 1) / (n + 1)


def main(min_importance: int = 2) -> None:
    m = pd.read_parquet(PROCESSED_DIR / "market_intraday.parquet").set_index("timestamp_utc").sort_index()
    close = m["ust10_fut_close"].dropna()
    lo, hi = close.index.min(), close.index.max() - pd.Timedelta(minutes=max(HORIZONS))
    cal = pd.read_parquet(PROCESSED_DIR / "events_calendar.parquet")
    cal["t"] = pd.to_datetime(cal.timestamp_utc, utc=True)
    all_days = set(cal.t.dt.tz_convert(ET).dt.date)
    ev = cal[(cal.importance >= min_importance) & (cal.t >= lo) & (cal.t <= hi)]
    times = pd.DatetimeIndex(ev.t.unique())
    rows = []
    for h in HORIZONS:
        s = build_sample(close, times, all_days, h)
        e, b = s[s.is_event].move, s[~s.is_event].move
        if len(e) < 3 or len(b) < 10:
            continue
        obs, p = perm_p(s)
        rows.append(dict(horizon_min=h, n_calendar_rows=len(ev), n_events=len(e), n_baseline=len(b), event_mean_bp=e.mean(),
                         event_median_bp=e.median(), baseline_mean_bp=b.mean(), ratio=e.mean() / b.mean(),
                         slot_matched_diff_bp=obs, perm_p_one_sided=p))
    res = pd.DataFrame(rows)
    out = PROJECT_ROOT / "reports" / "tables" / "event_study.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out, index=False)
    print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-importance", type=int, default=2)
    main(ap.parse_args().min_importance)
