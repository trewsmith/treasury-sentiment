"""Stress tests of the daily Reddit-tone result (2025+).

Variants of the Reddit measure: score-weighted (headline; weights use ~36h-later scores), unweighted, and
unweighted excluding r/wallstreetbets. For each:
  outcomes     d10y, d2y, d(10y-2y), all without the 2y control, plus d10y with it
  lags         t-1, t, t+1 jointly
  news split   before / after 2025-11-24 (before = essentially Fed-only news)
  press ctrl   adds press (non-Fed) tone and direction
  low-vol      interaction with lagged low-rate-vol regime (tests the difference, not separate fits)
  block boot   moving-block bootstrap p (block 10 days) for the main coefficient
Holm adjustment across every test in the table (except diagnostics marked boot).

Usage: PYTHONPATH=. python src/modeling/reddit_robustness.py
Output: reports/tables/reddit_robustness.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from src.modeling.daily_regression import CONTROLS, HAC_LAGS, NEWS, build_panel
from src.utils.paths import PROCESSED_DIR, TABLES_DIR

SPLIT = "2025-11-24"
MEASURES = {"weighted": "reddit_sent_wmean", "unweighted": "reddit_sent_mean", "unweighted_exwsb": "reddit_exwsb_sent_mean"}
BASE = [c for c in CONTROLS if c != "d2y_bp"]


def z(x):
    return ((x - x.mean()) / x.std()).fillna(0.0)


def run(d, y, xs, test, spec, measure):
    s = d[[y, *xs]].dropna()
    r = sm.OLS(s[y], sm.add_constant(s[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    return [dict(measure=measure, spec=spec, outcome=y, var=v, coef_bp_per_sd=r.params[v], se=r.bse[v], t=r.tvalues[v],
                 p=r.pvalues[v], n=int(r.nobs)) for v in test]


def block_boot_p(d, y, xs, v, n=2000, block=10, seed=0):
    """Two-sided bootstrap p: moving blocks, coefficient centered at its estimate."""
    s = d[[y, *xs]].dropna()
    Y, X = s[y].to_numpy(), np.column_stack([np.ones(len(s)), s[xs].to_numpy()])
    j = 1 + xs.index(v)
    b0 = np.linalg.lstsq(X, Y, rcond=None)[0][j]
    rng = np.random.default_rng(seed)
    T, k = len(s), int(np.ceil(len(s) / block))
    bs = []
    for _ in range(n):
        i = (rng.integers(0, T - block + 1, k)[:, None] + np.arange(block)).ravel()[:T]
        bs.append(np.linalg.lstsq(X[i], Y[i], rcond=None)[0][j])
    return float((np.sum(np.abs(np.array(bs) - b0) >= abs(b0)) + 1) / (n + 1)), float(b0), T


def main() -> None:
    df = build_panel()
    rv = df.d10y_bp.rolling(20).std().shift(1)
    df["low_vol"] = (rv <= rv.rolling(250, min_periods=120).median()).astype(float)
    f = pd.read_parquet(PROCESSED_DIR / "features_daily.parquet").set_index("date")
    d = df.loc["2025-01-01":].copy()
    for c in ("press_sent_mean", "press_ydir_mean"):
        d[c] = z(f[c].reindex(d.index))
    rows = []
    for name, col in MEASURES.items():
        d["r"] = z(f[col].reindex(d.index))
        d["r_lag1"], d["r_lead1"] = d.r.shift(1), d.r.shift(-1)
        d["r_x_lowvol"] = d.r * d.low_vol
        xs = ["r"] + NEWS + BASE
        for y in ("d10y_bp", "d2y_bp", "dslope_bp"):
            rows += run(d, y, xs, ["r"], "outcome", name)
        rows += run(d, "d10y_bp", xs + ["d2y_bp"], ["r"], "with_2y", name)
        rows += run(d, "d10y_bp", ["r_lag1", "r", "r_lead1"] + NEWS + BASE, ["r_lag1", "r", "r_lead1"], "lags", name)
        rows += run(d.loc[:SPLIT].iloc[:-1], "d10y_bp", xs, ["r"], "pre_split_fed_only_news", name)
        rows += run(d.loc[SPLIT:], "d10y_bp", xs, ["r"], "post_split", name)
        rows += run(d, "d10y_bp", ["r", "press_sent_mean", "press_ydir_mean"] + BASE, ["r", "press_sent_mean", "press_ydir_mean"], "press_control", name)
        rows += run(d, "d10y_bp", ["r", "r_x_lowvol", "low_vol"] + NEWS + BASE, ["r", "r_x_lowvol"], "lowvol_interaction", name)
        p, b, n = block_boot_p(d, "d10y_bp", xs, "r")
        rows.append(dict(measure=name, spec="block_boot", outcome="d10y_bp", var="r", coef_bp_per_sd=b, p=p, n=n))
    res = pd.DataFrame(rows)
    m = res.spec != "block_boot"
    res["p_holm"] = np.nan
    res.loc[m, "p_holm"] = multipletests(res.p[m], method="holm")[1]
    res.to_csv(TABLES_DIR / "reddit_robustness.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
