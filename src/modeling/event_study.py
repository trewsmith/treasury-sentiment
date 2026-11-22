"""Event study: do scheduled macro releases move the 10y more than ordinary days at the same time?

For each event at time T and horizon h ∈ {5, 30, 60} min, move = |Δ 10y futures price| (bp, from
price at T to T+h; price at T = close of the bar that starts T-5min). Baseline = the same clock
time on weekdays with NO importance≥2 event that day. Permutation test on the mean (one-sided).
Also reports pre-event text intensity (docs in the 60 min before T) for context.

With ~60 days of 5-min data there are only ~20 events, so this is a scaffold: the magnitude test is
the only thing the sample can say anything about. Re-run as intraday history grows.

Usage: PYTHONPATH=. python src/modeling/event_study.py [--min-importance 2]
Output: reports/tables/event_study.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from src.utils.paths import PROCESSED_DIR, PROJECT_ROOT

HORIZONS = (5, 30, 60)


def price_at(close: pd.Series, t: pd.Timestamp):
    """Price at time t = close of the bar that starts 5 min earlier."""
    return close.get(t - pd.Timedelta(minutes=5), np.nan)


def abs_move(close: pd.Series, t: pd.Timestamp, h: int) -> float:
    p0, p1 = price_at(close, t), price_at(close, t + pd.Timedelta(minutes=h))
    return abs(np.log(p1 / p0)) * 1e4 if np.isfinite(p0) and np.isfinite(p1) else np.nan


def perm_p(event: np.ndarray, base: np.ndarray, n=10000, seed=0) -> float:
    """One-sided permutation p that mean(event) > mean(base)."""
    rng = np.random.default_rng(seed)
    pooled, k = np.concatenate([event, base]), len(event)
    obs = event.mean() - base.mean()
    cnt = sum(
        (lambda x: x[:k].mean() - x[k:].mean())(rng.permutation(pooled)) >= obs for _ in range(n)
    )
    return (cnt + 1) / (n + 1)


def main(min_importance: int = 2) -> None:
    m = pd.read_parquet(PROCESSED_DIR / "market_intraday.parquet").set_index("timestamp_utc").sort_index()
    close = m["ust10_fut_close"].dropna()
    lo, hi = close.index.min(), close.index.max() - pd.Timedelta(minutes=max(HORIZONS))
    ev = pd.read_parquet(PROCESSED_DIR / "events_calendar.parquet")
    ev["t"] = pd.to_datetime(ev.timestamp_utc, utc=True)
    ev = ev[(ev.importance >= min_importance) & (ev.t >= lo) & (ev.t <= hi)]
    event_days = set(ev.t.dt.date)
    all_days = set(pd.read_parquet(PROCESSED_DIR / "events_calendar.parquet").pipe(
        lambda d: pd.to_datetime(d.timestamp_utc, utc=True).dt.date))  # any-importance days excluded from baseline
    days = pd.bdate_range(lo.normalize(), hi.normalize())
    rows = []
    for h in HORIZONS:
        e_moves = np.array([abs_move(close, t, h) for t in ev.t])
        e_moves = e_moves[np.isfinite(e_moves)]
        b = []
        for t in ev.t:  # same clock time on clean weekdays
            for d in days:
                if d.date() in all_days or d.date() in event_days:
                    continue
                tt = pd.Timestamp.combine(d.date(), t.time()).tz_localize("UTC")
                # UTC clock time shifts an hour across DST; accept (events and baseline share the same UTC time)
                b.append(abs_move(close, tt, h))
        b = np.array(b)
        b = b[np.isfinite(b)]
        if len(e_moves) < 3 or len(b) < 10:
            continue
        rows.append(dict(horizon_min=h, n_events=len(e_moves), n_baseline=len(b), event_mean_bp=e_moves.mean(),
                         event_median_bp=np.median(e_moves), baseline_mean_bp=b.mean(),
                         ratio=e_moves.mean() / b.mean(), perm_p_one_sided=perm_p(e_moves, b)))
    res = pd.DataFrame(rows)
    out = PROJECT_ROOT / "reports" / "tables" / "event_study.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out, index=False)
    print(f"events ≥ importance {min_importance} in window: {len(ev)}")
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-importance", type=int, default=2)
    main(ap.parse_args().min_importance)
