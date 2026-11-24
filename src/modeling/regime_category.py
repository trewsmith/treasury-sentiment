"""Regime-conditional and information-category daily analyses.

Category: Δ10y on one topic's yield-direction score at a time (inflation, fed, growth, labor, fiscal),
  news 2006– and news+Reddit 2025–, with full controls. Standardized on days the topic has docs,
  zero elsewhere (so coefficients are bp per 1 SD of a topic-day).
Regime: news (and Reddit, 2025–) factors split by regime, fit separately in each regime.
  Regimes use only past information: VIX above/below its trailing 250d median (lagged 1 day),
  trailing 20d realized 10y vol above/below its trailing 250d median (lagged), scheduled-event days.
Holm adjustment is applied across all text coefficients within each analysis × control set.

Usage: PYTHONPATH=. python src/modeling/regime_category.py
Output: reports/tables/regime_category.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

from src.modeling.daily_regression import CONTROLS, NEWS, REDDIT, build_panel, fit
from src.utils.paths import PROCESSED_DIR, PROJECT_ROOT

TOPICS = ["inflation", "fed", "growth", "labor", "fiscal"]


def topic_cols(df, f):
    cols = []
    for src in ("news", "reddit"):
        for t in TOPICS:
            c = f"{src}_{t}_ydir_mean"
            if c not in f:
                continue
            x = f[c].reindex(df.index)
            has = x.notna()
            z = ((x - x[has].mean()) / x[has].std()).where(has, 0.0)
            df[c] = z if has.sum() > 30 else np.nan
            cols.append(c)
    return cols


def main() -> None:
    df = build_panel()
    f = pd.read_parquet(PROCESSED_DIR / "features_daily.parquet").set_index("date")
    tcols = topic_cols(df, f)
    m = pd.read_csv(PROJECT_ROOT / "data/processed/market_daily.csv", parse_dates=["date"]).set_index("date").sort_index()
    lv = m.VIXCLS.reindex(df.index).ffill(limit=3)
    df["regime_vix_hi"] = (lv.shift(1) > lv.shift(1).rolling(250, min_periods=120).median()).astype(float)
    rv = df["d10y_bp"].rolling(20).std().shift(1)
    df["regime_vol_hi"] = (rv > rv.rolling(250, min_periods=120).median()).astype(float)
    valid_v = lv.shift(1).rolling(250, min_periods=120).median().notna()
    valid_r = rv.rolling(250, min_periods=120).median().notna()

    rows = []
    for label, ctrl in (("no_2y", [c for c in CONTROLS if c != "d2y_bp"]), ("with_2y", CONTROLS)):
        recent = df.loc["2025-01-01":]
        for t in TOPICS:
            n, r = f"news_{t}_ydir_mean", f"reddit_{t}_ydir_mean"
            if n in df and df[n].notna().any():
                rows += [dict(a, analysis="category") for a in fit(df, "d10y_bp", [n] + ctrl, label, f"cat_news_{t}")]
            if r in df and recent[r].notna().any():
                rows += [dict(a, analysis="category") for a in fit(recent, "d10y_bp", [r] + ctrl, label, f"cat_reddit_{t}_2025+")]
        regimes = [("vix", "regime_vix_hi", valid_v), ("rate_vol", "regime_vol_hi", valid_r)]
        for name, col, valid in regimes:
            for hi, tag in ((1.0, "high"), (0.0, "low")):
                sub = df[valid & (df[col] == hi)]
                rows += [dict(a, analysis="regime") for a in fit(sub, "d10y_bp", NEWS + ctrl, label, f"reg_{name}_{tag}_news")]
                s25 = sub.loc["2025-01-01":]
                rows += [dict(a, analysis="regime") for a in fit(s25, "d10y_bp", NEWS + REDDIT + ctrl, label, f"reg_{name}_{tag}_news+reddit_2025+")]
        for hi, tag in ((1.0, "event"), (0.0, "nonevent")):
            sub = df[df.event_day == hi]
            ctrl_e = [c for c in ctrl if c != "event_day"]
            rows += [dict(a, analysis="regime") for a in fit(sub, "d10y_bp", NEWS + ctrl_e, label, f"reg_{tag}_news")]
    res = pd.DataFrame(rows)
    res["p_holm"] = np.nan
    mask = res["var"].str.contains("sent|ydir", regex=True) & res.p.notna()
    for _, g in res[mask].groupby(["analysis", "controls"]):
        res.loc[g.index, "p_holm"] = multipletests(g.p, method="holm")[1]
    out = PROJECT_ROOT / "reports" / "tables" / "regime_category.csv"
    res.to_csv(out, index=False)
    pd.set_option("display.width", 220)
    keep = res[mask & (res.controls == "no_2y")]
    print(keep[["spec", "var", "coef_bp_per_sd", "t", "p", "p_holm", "n"]].round(3).to_string(index=False))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
