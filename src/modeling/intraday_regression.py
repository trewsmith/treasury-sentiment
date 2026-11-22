"""Intraday speed-of-incorporation baseline: do text factors predict 10y moves at 5/30/60 min?

y(h) = forward return of the 10y T-note futures from the close of 5-min bar t to the close of bar
t+h/5, in bp of price with the SIGN FLIPPED so + = yields up. (Futures cover more hours than ^TNX;
levels are not yields, but direction/timing are what matter here.)
X = text factors for the bucket starting at t (documents inside bar t are complete by its close, so
the forward window starts after them):
  news_ydir, reddit_ydir  (weighted yield-direction signal, 0 if no docs), ydir_pressure, shock_score
Controls: trailing 30-min return of the 10y future (momentum/reversal), plus trailing 30-min returns
of 2y futures, ES, DXY, WTI and a scheduled-event window dummy (event within ±30 min).
HAC (Newey-West) errors with lags ≥ the overlap of the forward window.

CAVEAT: Yahoo only serves ~60 days of 5-min data, so n is small until vendor data is added in
data/raw/intraday/vendor/. Treat as a scaffold; re-run as data accumulates.

Usage: PYTHONPATH=. python src/modeling/intraday_regression.py
Output: reports/tables/intraday_regression.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.utils.paths import PROCESSED_DIR, PROJECT_ROOT

HORIZONS = (5, 30, 60)  # minutes
BAR = 5
FACTORS = ["news_ydir", "reddit_ydir", "ydir_pressure", "shock_score"]
CONTROLS = ["ust10_trail30", "ust2_trail30", "es_trail30", "dxy_trail30", "wti_trail30", "event_window"]


def _ret(s: pd.Series, k: int) -> pd.Series:
    return np.log(s).diff(k) * 1e4


def build_panel() -> pd.DataFrame:
    m = pd.read_parquet(PROCESSED_DIR / "market_intraday.parquet").set_index("timestamp_utc").sort_index()
    idx = m.index
    out = pd.DataFrame(index=idx)
    f10 = m["ust10_fut_close"]
    for h in HORIZONS:
        k = h // BAR
        fwd = -(np.log(f10.shift(-k)) - np.log(f10)) * 1e4  # + = yields up
        ok = (pd.Series(idx, index=idx).shift(-k) - pd.Series(idx, index=idx)) == pd.Timedelta(minutes=h)  # no gaps
        out[f"y{h}"] = fwd.where(ok)
        lo, hi = out[f"y{h}"].quantile([0.005, 0.995])
        out[f"y{h}"] = out[f"y{h}"].clip(lo, hi)  # futures roll jumps / bad ticks
    k = 30 // BAR
    out["ust10_trail30"] = -_ret(f10, k)
    for name, col in (("ust2", "ust2_fut_close"), ("es", "es_fut_close"), ("dxy", "dxy_close"), ("wti", "wti_fut_close")):
        out[f"{name}_trail30"] = _ret(m[col], k)
    f = pd.read_parquet(PROCESSED_DIR / "features_intraday.parquet")
    f = f[f.bucket_freq == "5min"].set_index("bucket_start_utc").sort_index()
    text_end = f.index[(f.n_news + f.n_reddit) > 0].max()  # market bars after the last document carry no signal
    out = out[out.index <= text_end]
    f = f.rename(columns={"news_ydir_wmean": "news_ydir", "reddit_ydir_wmean": "reddit_ydir"})
    out = out.join(f[["news_ydir", "reddit_ydir", "ydir_pressure", "shock_score"]], how="left")
    out[["news_ydir", "reddit_ydir", "ydir_pressure", "shock_score"]] = out[
        ["news_ydir", "reddit_ydir", "ydir_pressure", "shock_score"]
    ].fillna(0.0)
    ev = pd.read_parquet(PROCESSED_DIR / "events_calendar.parquet")
    ev_t = pd.to_datetime(ev.loc[ev.importance >= 3, "timestamp_utc"], utc=True)
    near = np.zeros(len(out), dtype=bool)
    pos = out.index.values.astype("datetime64[ns]")
    for t in ev_t.values.astype("datetime64[ns]"):
        near |= np.abs(pos - t) <= np.timedelta64(30, "m")
    out["event_window"] = near.astype(float)
    # drop rows with no trading in the 10y future; standardize factors on active rows
    out = out[out["ust10_trail30"].notna() | out["y5"].notna()]  # keep bars where the 10y future traded
    for c in FACTORS:
        sd = out[c].std()
        if sd and sd > 0:
            out[c] = out[c] / sd
    return out


def fit(df: pd.DataFrame, h: int, xs: list[str], spec: str) -> list[dict]:
    d = df[[f"y{h}", *xs]].dropna()
    if len(d) < 50:
        return []
    res = sm.OLS(d[f"y{h}"], sm.add_constant(d[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": max(h // BAR, 1) + 12})
    return [
        dict(spec=spec, horizon_min=h, var=v, coef_bp_per_sd=res.params[v], se=res.bse[v], t=res.tvalues[v],
             p=res.pvalues[v], n=int(res.nobs), adj_r2=res.rsquared_adj)
        for v in xs
        if v in FACTORS
    ]


def main() -> None:
    df = build_panel()
    print(f"panel: {len(df):,} 5-min bars, {df.index.min()} → {df.index.max()}")
    print(f"bars with news docs: {(df.news_ydir != 0).sum():,}; with reddit docs: {(df.reddit_ydir != 0).sum():,}")
    rows = []
    for h in HORIZONS:
        rows += fit(df, h, ["news_ydir", "ydir_pressure"] + CONTROLS, "news_only")
        rows += fit(df, h, ["news_ydir", "reddit_ydir", "shock_score"] + CONTROLS, "news_plus_reddit")
    res = pd.DataFrame(rows)
    out = PROJECT_ROOT / "reports" / "tables" / "intraday_regression.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out, index=False)
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
