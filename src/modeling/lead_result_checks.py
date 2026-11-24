"""Post hoc checks of the lead result: same-day Reddit tone and the daily 2-year change, 2025+.

reddit_robustness.py stress-tests the 10-year; this repeats those checks with d2y_bp as the outcome and adds timing.
All of it is exploratory: the 2-year outcome was chosen after seeing results.
  controls     none / baseline / baseline + lagged d2y / + log Reddit volume / + press tone and direction
  lags         tone at t-1, t, t+1 jointly
  splits       before / after 2025-11-24, no major-event days, low-rate-vol interaction
  timing       posts before 08:00 ET (overnight, incl. prior day after 15:30 and weekends) vs. 08:00-15:30 ET of the
               yield date. The overnight part is dated before the day's US session, so it cannot react to that session, but it can react to overnight moves in the same yield change.
  lead_lag     d2y on day t+k, text on day t, k = -2..+2 (controls from the yield day)
  hac10/hac20  wider Newey-West windows; loqo = leave one calendar quarter out (min/max coefficient, max p)
  block_boot   moving-block bootstrap p; circ_shift = circular-shift placebo p (all shifts >= 20 days)
  oos          rolling 250-day one-step OOS R2 vs. controls only, text scaled with past data only
Holm adjustment covers every coefficient test for a spec in HOLM within one family per table (diagnostics excluded).

Usage: PYTHONPATH=. python src/modeling/lead_result_checks.py
Output: reports/tables/lead_result_checks.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from src.modeling.daily_regression import CONTROLS, HAC_LAGS, NEWS, build_panel
from src.modeling.reddit_robustness import BASE, MEASURES, SPLIT, block_boot_p, z
from src.utils.paths import DOCUMENTS_SCORED_PARQUET, PROCESSED_DIR, TABLES_DIR

Y = "d2y_bp"
HOLM = ["no_controls", "baseline", "lagged_yield", "volume", "press_control", "lags", "pre_split", "post_split",
        "no_event_days", "lowvol_interaction", "timing_separate", "timing_joint", "lead_lag"]


def fit(d, xs, test, spec, measure, lags=HAC_LAGS, y=Y):
    s = d[[y, *xs]].dropna()
    r = sm.OLS(s[y], sm.add_constant(s[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return [dict(measure=measure, spec=spec, var=v, coef_bp_per_sd=r.params[v], se=r.bse[v], t=r.tvalues[v], p=r.pvalues[v],
                 n=int(r.nobs)) for v in test]


def timing_measures() -> pd.DataFrame:
    """Daily Reddit tone split by posting time relative to the yield date (unweighted, with and without WSB)."""
    d = pd.read_parquet(DOCUMENTS_SCORED_PARQUET, columns=["source_type", "source_name", "timestamp_utc", "yield_date",
                                                           "finbert_sentiment_score", "is_relevant"])
    d = d[(d.source_type == "reddit") & d.is_relevant & d.yield_date.notna()]
    et = d.timestamp_utc.dt.tz_convert("America/New_York").dt.tz_localize(None)
    early = et < (pd.to_datetime(d.yield_date) + pd.Timedelta(hours=8))
    out = {}
    for tag, m in (("unweighted", pd.Series(True, index=d.index)), ("unweighted_exwsb", d.source_name != "r/wallstreetbets")):
        out[f"{tag}_overnight"] = d[m & early].groupby("yield_date").finbert_sentiment_score.mean()
        out[f"{tag}_session"] = d[m & ~early].groupby("yield_date").finbert_sentiment_score.mean()
    f = pd.DataFrame(out)
    f.index = pd.to_datetime(f.index)
    return f


def circ_shift_p(d, xs):
    s = d[[Y, *xs]].dropna()
    res = lambda c: s[c] - sm.OLS(s[c], sm.add_constant(s[[x for x in xs if x != "r"]])).fit().fittedvalues
    y, r = res(Y).to_numpy(), res("r").to_numpy()
    stat = lambda q: q @ y / (q @ q)
    b0 = stat(r)
    null = np.array([stat(np.roll(r, k)) for k in range(20, len(r) - 20)])
    return float((np.sum(np.abs(null) >= abs(b0)) + 1) / (len(null) + 1)), float(b0), len(s)


def oos(d, raw, window=250):
    s = d[[Y, *BASE]].copy()
    past = raw.shift(1).expanding(min_periods=30)
    s["x"] = (raw - past.mean()) / past.std()
    s = s.dropna()
    f = lambda tr, te, xs: float(np.r_[1.0, te[xs].to_numpy()] @ np.linalg.lstsq(np.column_stack([np.ones(len(tr)), tr[xs]]), tr[Y], rcond=None)[0])
    eb, ef = [], []
    for i in range(window, len(s)):
        tr, te = s.iloc[i - window:i], s.iloc[i]
        eb.append(te[Y] - f(tr, te, BASE))
        ef.append(te[Y] - f(tr, te, BASE + ["x"]))
    return 1 - np.sum(np.square(ef)) / np.sum(np.square(eb)), len(eb)


def main() -> None:
    df = build_panel()
    rv = df.d2y_bp.rolling(20).std().shift(1)
    df["low_vol"] = (rv <= rv.rolling(250, min_periods=120).median()).astype(float)
    df["d2y_lag1"] = df.d2y_bp.shift(1)
    f = pd.read_parquet(PROCESSED_DIR / "features_daily.parquet").set_index("date")
    d = df.loc["2025-01-01":].copy()
    for c in ("press_sent_mean", "press_ydir_mean"):
        d[c] = z(f[c].reindex(d.index))
    d["log_n"] = z(np.log1p(f.n_reddit_relevant.reindex(d.index)))
    tm = timing_measures().reindex(d.index)
    q = d.index.to_period("Q")
    rows = []
    for name, col in MEASURES.items():
        raw = f[col].reindex(d.index)
        d["r"] = z(raw)
        d["r_lag1"], d["r_lead1"], d["r_x_lowvol"] = d.r.shift(1), d.r.shift(-1), d.r * d.low_vol
        xs = ["r"] + NEWS + BASE
        add = lambda data, x, test, spec, **k: rows.extend(fit(data, x, test, spec, name, **k))
        add(d, ["r"], ["r"], "no_controls")
        add(d, xs, ["r"], "baseline")
        add(d, xs + ["d2y_lag1"], ["r"], "lagged_yield")
        add(d, xs + ["log_n"], ["r", "log_n"], "volume")
        add(d, ["r", "press_sent_mean", "press_ydir_mean"] + BASE, ["r", "press_sent_mean", "press_ydir_mean"], "press_control")
        add(d, ["r_lag1", "r", "r_lead1"] + NEWS + BASE, ["r_lag1", "r", "r_lead1"], "lags")
        add(d.loc[:SPLIT].iloc[:-1], xs, ["r"], "pre_split")
        add(d.loc[SPLIT:], xs, ["r"], "post_split")
        add(d[d.event_day == 0], [x for x in xs if x != "event_day"], ["r"], "no_event_days")
        add(d, ["r", "r_x_lowvol", "low_vol"] + NEWS + BASE, ["r", "r_x_lowvol"], "lowvol_interaction")
        if f"{name}_overnight" in tm:
            d["overnight"], d["session"] = z(tm[f"{name}_overnight"]), z(tm[f"{name}_session"])
            for v in ("overnight", "session"):
                add(d, [v] + NEWS + BASE, [v], "timing_separate")
            add(d, ["overnight", "session"] + NEWS + BASE, ["overnight", "session"], "timing_joint")
        for k in (-2, -1, 0, 1, 2):
            g = df[[Y, *BASE]].shift(-k).loc["2025-01-01":].copy()
            g[f"k={k}"] = d.r
            add(g, [f"k={k}"] + BASE, [f"k={k}"], "lead_lag")
        for L in (10, 20):
            add(d, xs, ["r"], f"hac{L}", lags=L)
        lo = [fit(d[q != p], xs, ["r"], "", name)[0] for p in q.unique()]
        rows += [dict(measure=name, spec="loqo_min", var="r", coef_bp_per_sd=min(x["coef_bp_per_sd"] for x in lo)),
                 dict(measure=name, spec="loqo_max", var="r", coef_bp_per_sd=max(x["coef_bp_per_sd"] for x in lo), p=max(x["p"] for x in lo))]
        for spec, (p, b, n) in (("block_boot", block_boot_p(d, Y, xs, "r")), ("circ_shift", circ_shift_p(d, xs))):
            rows.append(dict(measure=name, spec=spec, var="r", coef_bp_per_sd=b, p=p, n=n))
        r2, n = oos(d, raw)
        rows.append(dict(measure=name, spec="oos_r2", var="OOS_R2", coef_bp_per_sd=r2, n=n))
    res = pd.DataFrame(rows)
    m = res.spec.isin(HOLM)
    res["p_holm"] = np.nan
    res.loc[m, "p_holm"] = multipletests(res.p[m], method="holm")[1]
    res.to_csv(TABLES_DIR / "lead_result_checks.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
