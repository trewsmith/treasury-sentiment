"""Daily baseline: do text-derived factors explain the 10y yield change?

y_t = Δ DGS10 on day t (basis points), regressed on same-day sentiment factors (documents are
dated by `yield_date`, so day-t factors only use text that could affect day t's close), plus
controls: Δ2y, ΔVIX, Δlog S&P 500, Δlog broad dollar, Δlog WTI, and a scheduled-event dummy.
Standardized factors → coefficients are bp per 1 SD. Newey-West (HAC, 5 lags) standard errors.

Specs
  news_only      2006–: news tone + news yield-direction
  news_vs_reddit 2025–: adds Reddit factors; Wald test of the Reddit block = incremental power
  placebo_lead   news yield-direction at t+1 predicting Δ10y at t (should be ~0; flags leakage)
Each runs with and without the Δ2y control (Δ2y absorbs most policy-driven variation).

Usage: PYTHONPATH=. python src/modeling/daily_regression.py
Output: reports/tables/daily_regression.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.utils.paths import MARKET_DAILY_PATH, PROCESSED_DIR, PROJECT_ROOT

NEWS = ["news_sent_wmean", "news_ydir_wmean"]
REDDIT = ["reddit_sent_wmean", "reddit_ydir_wmean"]
CONTROLS = ["d2y_bp", "dvix", "dsp500", "ddollar", "doil", "event_day"]
HAC_LAGS = 5


def build_panel() -> pd.DataFrame:
    m = pd.read_csv(MARKET_DAILY_PATH, parse_dates=["date"]).set_index("date").sort_index()
    lv = m[["DGS10", "DGS2", "VIXCLS", "SP500", "DTWEXBGS", "DCOILWTICO"]].dropna(subset=["DGS10"]).ffill(limit=3)
    px = pd.DataFrame(
        {
            "d10y_bp": lv.DGS10.diff() * 100,
            "d2y_bp": lv.DGS2.diff() * 100,
            "dvix": lv.VIXCLS.diff(),
            "dsp500": np.log(lv.SP500).diff() * 100,
            "ddollar": np.log(lv.DTWEXBGS).diff() * 100,
            "doil": np.log(lv.DCOILWTICO.where(lv.DCOILWTICO > 0)).diff() * 100,
        }
    )
    ev = pd.read_parquet(PROCESSED_DIR / "events_calendar.parquet")
    big = pd.to_datetime(ev.loc[ev.importance >= 3, "event_date"]).dt.normalize().unique()
    px["event_day"] = px.index.isin(big).astype(float)
    f = pd.read_parquet(PROCESSED_DIR / "features_daily.parquet").set_index("date")
    df = px.join(f, how="inner")
    sig = [c for c in NEWS + REDDIT if c in df]
    df[sig] = df[sig].fillna(0.0)  # no docs that day → neutral
    for c in sig:  # standardize on days that have documents
        has = df["n_reddit_relevant" if c.startswith("reddit") else "n_news_relevant"] > 0
        mu, sd = df.loc[has, c].mean(), df.loc[has, c].std()
        df[c] = ((df[c] - mu) / sd).where(has, 0.0)
    df["news_ydir_lead1"] = df["news_ydir_wmean"].shift(-1)
    return df


def fit(df, y, xs, label, spec, wald=None):
    d = df[[y, *xs]].dropna()
    res = sm.OLS(d[y], sm.add_constant(d[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    out = [
        dict(spec=spec, controls=label, var=v, coef_bp_per_sd=res.params[v], se=res.bse[v], t=res.tvalues[v],
             p=res.pvalues[v], n=int(res.nobs), r2=res.rsquared, adj_r2=res.rsquared_adj)
        for v in xs
        if v not in CONTROLS
    ]
    if wald:
        w = res.wald_test(", ".join(f"{v} = 0" for v in wald), use_f=True, scalar=True)
        out.append(dict(spec=spec, controls=label, var="WALD:" + "+".join(wald), t=float(w.statistic), p=float(w.pvalue),
                        n=int(res.nobs), r2=res.rsquared, adj_r2=res.rsquared_adj))
    return out


def main() -> None:
    df = build_panel()
    rows = []
    for label, ctrl in (("no_2y", [c for c in CONTROLS if c != "d2y_bp"]), ("with_2y", CONTROLS)):
        rows += fit(df, "d10y_bp", NEWS + ctrl, label, "news_only")
        rows += fit(df, "d10y_bp", ["news_ydir_lead1"] + ctrl, label, "placebo_lead")
        recent = df.loc["2025-01-01":]
        rows += fit(recent, "d10y_bp", NEWS + ctrl, label, "news_2025+")
        rows += fit(recent, "d10y_bp", NEWS + REDDIT + ctrl, label, "news_vs_reddit_2025+", wald=REDDIT)
    res = pd.DataFrame(rows)
    out = PROJECT_ROOT / "reports" / "tables" / "daily_regression.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out, index=False)
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
