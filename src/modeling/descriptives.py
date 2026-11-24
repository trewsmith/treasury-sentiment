"""Descriptive tables for the write-up: regression variables, document counts, hand/silver labels.

Usage: PYTHONPATH=. python src/modeling/descriptives.py
Output: reports/tables/desc_variables.csv, desc_documents.csv, desc_labels.csv
"""
from __future__ import annotations

import pandas as pd

from src.modeling.daily_regression import NEWS, REDDIT, build_panel
from src.nlp import yield_classifier as yc
from src.utils.paths import DOCUMENTS_SCORED_PARQUET, PROCESSED_DIR, PROJECT_ROOT, TABLES_DIR


def main() -> None:
    df = build_panel()
    f = pd.read_parquet(PROCESSED_DIR / "features_daily.parquet").set_index("date")
    market = ["d10y_bp", "d2y_bp", "dslope_bp", "dvix", "dsp500", "ddollar", "doil", "event_day"]
    text = NEWS + ["press_sent_mean", "press_ydir_mean"] + REDDIT + ["reddit_sent_mean", "reddit_exwsb_sent_mean"]
    text += ["n_news_relevant", "n_press", "n_reddit_relevant"]
    rows = []
    for w, start in (("2006+", "2006"), ("2025+", "2025"), ("2025-11-24+", "2025-11-24")):
        for c in market + text:
            if w == "2006+" and "reddit" in c:
                continue
            x = (df[c] if c in market else f[c].reindex(df.index)).loc[start:].dropna()  # text in raw units
            rows.append(dict(window=w, var=c, n=len(x), mean=x.mean(), sd=x.std(), min=x.min(), p25=x.quantile(.25),
                             median=x.median(), p75=x.quantile(.75), max=x.max()))
    v = pd.DataFrame(rows)
    v.to_csv(TABLES_DIR / "desc_variables.csv", index=False)

    d = pd.read_parquet(DOCUMENTS_SCORED_PARQUET, columns=["source_type", "source_name", "timestamp_utc", "timestamp_is_date_only",
                                                           "is_relevant", "yield_date", "finbert_sentiment_score", "yield_direction_signal"])
    g = d.groupby(["source_type", "source_name"])
    doc = g.agg(docs=("is_relevant", "size"), relevant=("is_relevant", "sum"), date_only_share=("timestamp_is_date_only", "mean"),
                first=("timestamp_utc", "min"), last=("timestamp_utc", "max"))
    r = d[d.is_relevant].groupby(["source_type", "source_name"])
    doc["finbert_mean"], doc["ydir_mean"] = r.finbert_sentiment_score.mean(), r.yield_direction_signal.mean()
    doc["first"], doc["last"] = doc["first"].dt.date, doc["last"].dt.date
    doc.reset_index().to_csv(TABLES_DIR / "desc_documents.csv", index=False)

    lab = yc.load_labels()
    ids = {b: set(pd.read_csv(PROJECT_ROOT / f"data/labels/hand_batch{b}_key.csv").doc_id) for b in (1, 2, 3)}
    lab["set"] = "silver"
    hand = lab.labeler != "claude-silver"
    for b, s in ids.items():
        lab.loc[hand & lab.doc_id.isin(s), "set"] = f"hand_batch{b}"
    pd.crosstab(lab["set"], lab.label, margins=True).reset_index().to_csv(TABLES_DIR / "desc_labels.csv", index=False)
    print(v.round(3).to_string(index=False), doc.to_string(), pd.crosstab(lab["set"], lab.label), sep="\n\n")


if __name__ == "__main__":
    main()
