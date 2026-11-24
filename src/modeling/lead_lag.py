"""Does text lead, coincide with, or follow 10y yield moves? (daily, 2025-11-24+ and 2025+)

Separate regressions of d10y on day t+k (k = -2..+2) on text dated t, controls (no 2y) measured on the same
day as the yield change. k<0: text FOLLOWS yields (reporting / reaction). k=0: same day. k>0: text leads.
Press is split by timestamp quality: placeholder-time items are dated to the NEXT yield date by construction,
so their k=-1 loading is partly mechanical; `press_timed` (real clock times) is the clean version.
Holm within window over all (measure, k).

Usage: PYTHONPATH=. python src/modeling/lead_lag.py
Output: reports/tables/lead_lag.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from src.modeling.daily_regression import CONTROLS, HAC_LAGS, build_panel
from src.utils.paths import DOCUMENTS_SCORED_PARQUET, TABLES_DIR

BASE = [c for c in CONTROLS if c != "d2y_bp"]


def measures() -> pd.DataFrame:
    d = pd.read_parquet(DOCUMENTS_SCORED_PARQUET, columns=["source_type", "source_name", "timestamp_is_date_only", "yield_date",
                                                           "yield_direction_signal", "finbert_sentiment_score", "is_relevant"])
    d = d[d.is_relevant & d.yield_date.notna()]
    press = (d.source_type == "news") & (d.source_name != "federal_reserve")
    groups = {"press_all": press, "press_timed": press & ~d.timestamp_is_date_only,
              "press_placeholder": press & d.timestamp_is_date_only,
              "fed": (d.source_name == "federal_reserve"), "reddit": d.source_type == "reddit",
              "reddit_exwsb": (d.source_type == "reddit") & (d.source_name != "r/wallstreetbets")}
    out = {}
    for g, m in groups.items():
        x = d[m].groupby("yield_date")
        out[f"{g}_dir"] = x.yield_direction_signal.mean()
        out[f"{g}_tone"] = x.finbert_sentiment_score.mean()
    f = pd.DataFrame(out)
    f.index = pd.to_datetime(f.index)
    return f


def main() -> None:
    df = build_panel()
    m = measures()
    rows = []
    for w, start in (("2025-11-24+", "2025-11-24"), ("2025+", "2025-01-01")):
        for c in m:
            for k in (-2, -1, 0, 1, 2):
                d = df[["d10y_bp", *BASE]].shift(-k)
                d["x"] = m[c].reindex(d.index)
                d = d.loc[start:].dropna()
                if len(d) < 60 or d.x.std() == 0:
                    continue
                d["x"] = (d.x - d.x.mean()) / d.x.std()
                r = sm.OLS(d.d10y_bp, sm.add_constant(d[["x", *BASE]])).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
                rows.append(dict(window=w, measure=c, k=k, coef_bp_per_sd=r.params["x"], se=r.bse["x"], t=r.tvalues["x"], p=r.pvalues["x"], n=len(d)))
    res = pd.DataFrame(rows)
    for _, g in res.groupby("window"):
        res.loc[g.index, "p_holm"] = multipletests(g.p, method="holm")[1]
    res.to_csv(TABLES_DIR / "lead_lag.csv", index=False)
    for w, g in res.groupby("window"):
        print(w)
        print(g.assign(cell=g.coef_bp_per_sd.round(2).astype(str) + " (" + g.p_holm.round(3).astype(str) + ")").pivot(index="measure", columns="k", values="cell").to_string())
        print(g.groupby("measure").n.max().to_dict())


if __name__ == "__main__":
    main()
