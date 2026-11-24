"""Hourly extension of the intraday test: does text in hour t predict the 10y over the next hour(s)?

Uses Yahoo hourly bars (~730 days), so the sample covers all of 2025+ rather than ~3 months.
y_k = log return of 10y futures from the close of hour t to the close of hour t+k, sign flipped (+ = yields
up), k in {1, 2, 4}; k=0 is the contemporaneous hour (not predictive, for timing comparison). k=-1 is the
PRIOR hour: a placebo / reverse-causality check (does text follow yields?). Gaps and returns on the roll
(|z| beyond the 0.1/99.9 pct) are winsorized. HAC errors.
Text: press (non-Fed news with real timestamps), Fed documents are excluded (hour-level stamps unreliable);
Reddit with and without r/wallstreetbets, unweighted.

Usage: PYTHONPATH=. python src/modeling/hourly_regression.py
Output: reports/tables/hourly_regression.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from src.utils.paths import FEATURES_INTRADAY_PARQUET, MARKET_HOURLY_PARQUET, PROCESSED_DIR, TABLES_DIR

TEXT = ["press_ydir_mean", "press_sent_mean", "reddit_ydir_mean", "reddit_sent_mean"]
TEXT_X = ["press_ydir_mean", "press_sent_mean", "reddit_exwsb_ydir_mean", "reddit_exwsb_sent_mean"]
CONTROLS = ["ust10_lag", "ust2_lag", "es_lag", "dxy_lag", "wti_lag", "event_hour"]
H = pd.Timedelta(hours=1)


def build_panel() -> pd.DataFrame:
    m = pd.read_parquet(MARKET_HOURLY_PARQUET).set_index("timestamp_utc").sort_index()
    m = m.reindex(pd.date_range(m.index.min(), m.index.max(), freq="1h", tz="UTC"))
    p = np.log(m["ust10_fut_close"])
    out = pd.DataFrame(index=m.index)
    for k in (1, 2, 4):
        out[f"y{k}"] = -(p.shift(-k) - p) * 1e4
    out["y0"] = -(p - p.shift(1)) * 1e4
    out["y-1"] = out["y0"].shift(1)
    for c in [c for c in out if c.startswith("y")]:
        lo, hi = out[c].quantile([0.001, 0.999])
        out[c] = out[c].clip(lo, hi)
    # controls known at the close of hour t
    out["ust10_lag"] = out["y0"]
    for n, col in (("ust2", "ust2_fut_close"), ("es", "es_fut_close"), ("dxy", "dxy_close"), ("wti", "wti_fut_close")):
        out[f"{n}_lag"] = np.log(m[col].where(m[col] > 0)).diff() * 1e4
    ev = pd.read_parquet(PROCESSED_DIR / "events_calendar.parquet")
    t = pd.to_datetime(ev.loc[ev.importance >= 3, "timestamp_utc"], utc=True).dt.floor("h").unique()
    out["event_hour"] = (out.index.isin(t) | (out.index + H).isin(t)).astype(float)
    f = pd.read_parquet(FEATURES_INTRADAY_PARQUET)
    f = f[f.bucket_freq == "60min"].set_index("bucket_start_utc")
    end = f.index[f.n_reddit > 0].max()
    cols = sorted(set(TEXT + TEXT_X))
    out = out.join(f[cols + ["n_press", "n_reddit"]], how="inner").loc[pd.Timestamp("2025-01-01", tz="UTC"):end]
    out = out[out["y0"].notna() | out["y1"].notna()]
    for c in cols:
        has = out[c].notna()
        out[c] = ((out[c] - out.loc[has, c].mean()) / out.loc[has, c].std()).where(has, 0.0)
    return out


def fit(df, y, text, ctrl, spec):
    d = df[[y, *text, *ctrl]].dropna()
    r = sm.OLS(d[y], sm.add_constant(d[text + ctrl])).fit(cov_type="HAC", cov_kwds={"maxlags": 24})
    return [dict(spec=spec, outcome=y, var=v, coef_bp_per_sd=r.params[v], se=r.bse[v], t=r.tvalues[v], p=r.pvalues[v],
                 n=int(r.nobs), adj_r2=r.rsquared_adj) for v in text]


def main() -> None:
    df = build_panel()
    print(f"{len(df):,} hours {df.index.min()} to {df.index.max()}; hours with press {(df.n_press > 0).sum():,}, reddit {(df.n_reddit > 0).sum():,}")
    rows = []
    for spec, text in (("all_reddit", TEXT), ("ex_wsb", TEXT_X)):
        for k in (1, 2, 4):
            rows += fit(df, f"y{k}", text, CONTROLS, spec)
        rows += fit(df, "y0", text, ["event_hour"], spec)
        rows += fit(df, "y-1", text, ["event_hour"], spec)
    res = pd.DataFrame(rows)
    res["p_holm"] = np.nan  # predictive horizons only
    pred = res.outcome.isin(["y1", "y2", "y4"])
    for _, g in res[pred].groupby("spec"):
        res.loc[g.index, "p_holm"] = multipletests(g.p, method="holm")[1]
    res.to_csv(TABLES_DIR / "hourly_regression.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
