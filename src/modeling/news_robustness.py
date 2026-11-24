"""News-side robustness and the press-covered news vs. Reddit comparison.

Part 1 (timing/content of Fed documents, long sample). Date-only Fed items (stored at 00:00 ET; all 2006-2009)
count as same-day in the baseline. Variants: moved to the next yield date, dropped, sample from 2010, and
topic-tagged news only (drops enforcement actions, bank orders etc. that carry no macro topic).
Part 2 (2025+ windows). news = NEWS factors; press = non-Fed news only. For each window, the joint test of
each text block given the other, so neither source is treated as the default. Factors are re-standardized
inside each window. mde80 = 2.8 x SE: the effect detectable with 80% power at the 5% level.

Usage: PYTHONPATH=. python src/modeling/news_robustness.py
Output: reports/tables/news_robustness.csv, reports/tables/news_vs_reddit_windows.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from src.features.pipeline import build_daily, load_features_config, prepare, trading_calendar
from src.modeling.daily_regression import CONTROLS, HAC_LAGS, NEWS, REDDIT, build_panel
from src.utils.paths import DOCUMENTS_SCORED_PARQUET, TABLES_DIR

BASE = [c for c in CONTROLS if c != "d2y_bp"]
CTRL = {"no_2y": BASE, "with_2y": CONTROLS}
WINDOWS = {"all_2025+ (secondary)": ("2025-01-01", None), "press_covered_2025-11-24+ (main)": ("2025-11-24", None),
           "before_2025-11-24": ("2025-01-01", "2025-11-23"), "excl_2025Q2Q3": "gap"}
PRESS = ["press_sent_mean", "press_ydir_mean"]


def ols(d, y, xs):
    s = d[[y, *xs]].dropna()
    return sm.OLS(s[y], sm.add_constant(s[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})


def holm(df, by):
    df["p_holm"] = np.nan
    ok = df.p.notna()
    for _, g in df[ok].groupby(by):
        df.loc[g.index, "p_holm"] = multipletests(g.p, method="holm")[1]
    return df


def variants(docs):
    fed = (docs.source_name == "federal_reserve") & docs.timestamp_is_date_only
    cal = trading_calendar().to_numpy(dtype="datetime64[ns]")
    nxt = docs.copy()
    yd = nxt.loc[fed, "yield_date"].to_numpy(dtype="datetime64[ns]")
    i = np.searchsorted(cal, yd, side="right")
    nxt.loc[fed, "yield_date"] = pd.to_datetime(cal[np.minimum(i, len(cal) - 1)]).astype(nxt.yield_date.dtype)
    topical = (docs.source_type != "news") | (docs.n_topics > 0)
    print(f"date-only Fed items: {int(fed.sum()):,}; news without a macro topic: {int((~topical).sum()):,} of {int((docs.source_type == 'news').sum()):,}")
    return {"baseline": docs, "fed_midnight_next_day": nxt, "fed_midnight_dropped": docs[~fed], "topical_news_only": docs[topical]}


def main() -> None:
    cfg = load_features_config()
    docs = pd.read_parquet(DOCUMENTS_SCORED_PARQUET)
    rows = []
    for name, d in variants(docs).items():
        f = build_daily(prepare(d, cfg), cfg).set_index("date")
        df = build_panel(f)
        if name == "baseline":
            base_f = f
        samples = [("2006+", df), ("2010+", df.loc["2010":])] + ([("2025+", df.loc["2025":])] if name == "topical_news_only" else [])
        for sname, s in samples:
            for label, ctrl in CTRL.items():
                r = ols(s, "d10y_bp", NEWS + ctrl)
                rows += [dict(variant=name, sample=sname, controls=label, var=v, coef_bp_per_sd=r.params[v], se=r.bse[v],
                              t=r.tvalues[v], p=r.pvalues[v], n=int(r.nobs)) for v in NEWS]
    r1 = holm(pd.DataFrame(rows), "controls")
    r1.to_csv(TABLES_DIR / "news_robustness.csv", index=False)

    df = build_panel(base_f)
    for c in NEWS + REDDIT:
        df[c] = df[f"{c}_raw"]
    for c in PRESS:
        df[c] = base_f[c].reindex(df.index)
    df["n_press"] = base_f["n_press"].reindex(df.index)
    rows = []
    for w, b in WINDOWS.items():
        s = df.loc["2025-01-01":] if b == "gap" else df.loc[b[0]:b[1]]
        if b == "gap":
            s = s[(s.index < "2025-04-01") | (s.index >= "2025-10-01")]
        s = s.copy()
        for c in NEWS + REDDIT + PRESS:
            s[c] = ((s[c] - s[c].mean()) / s[c].std()).fillna(0.0)
        for label, ctrl in CTRL.items():
            for nset, news in (("news", NEWS), ("press", PRESS)):
                r = ols(s, "d10y_bp", news + REDDIT + ctrl)
                common = dict(window=w, controls=label, news_set=nset, n=int(r.nobs), share_days_press=float((s.n_press > 0).mean()))
                rows += [dict(common, kind="coef", var=v, coef_bp_per_sd=r.params[v], se=r.bse[v], t=r.tvalues[v],
                              p=r.pvalues[v], mde80=2.8 * r.bse[v]) for v in news + REDDIT]
                for nm, blk in ((f"{nset}_block|reddit", news), ("reddit_block|" + nset, REDDIT)):
                    k = r.wald_test(", ".join(f"{v} = 0" for v in blk), use_f=True, scalar=True)
                    rows.append(dict(common, kind="block", var=nm, t=float(k.statistic), p=float(k.pvalue)))
    r2 = holm(pd.DataFrame(rows), ["controls", "kind"])
    r2.to_csv(TABLES_DIR / "news_vs_reddit_windows.csv", index=False)
    pd.set_option("display.width", 220)
    print(r1.round(3).to_string(index=False))
    print(r2.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
