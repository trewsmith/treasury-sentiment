"""Blinded hand-labeling workflow for yield-direction labels.

  make   : write a blinded sheet (no silver label, no stratum) of N rows
  make-enriched : like make, but samples NEW docs (not in any label file) from documents_scored,
                  oversampling likely-down and uncertain-up docs, plus a random slice for base rates
  merge  : merge completed hand labels into yield_direction_labels.csv
           and report agreement vs. the silver labels (if any)
  Labels may be up/down/neutral or the short codes p/n/u (p=up, n=down, u=neutral).

Usage:
  PYTHONPATH=. python src/labeling/hand_labels.py make --n 100 --batch 1
  PYTHONPATH=. python src/labeling/hand_labels.py make-enriched --n 120 --batch 2
  PYTHONPATH=. python src/labeling/hand_labels.py merge --batch 1 --labeler trew
"""
import argparse
from datetime import date
from pathlib import Path

import pandas as pd

D = Path("data/labels")
SAMPLE = D / "yield_direction_sample.csv"
LABELS = D / "yield_direction_labels.csv"
VALID = {"up", "down", "neutral"}
ALIASES = {"p": "up", "n": "down", "u": "neutral"}  # Trew's short codes (batch 1)


def sheet(batch): return D / f"hand_batch{batch}.csv"
def key(batch): return D / f"hand_batch{batch}_key.csv"  # silver + stratum, do not open while labeling


def make(n, batch, seed):
    s = pd.read_csv(SAMPLE)
    done = set()
    for p in D.glob("hand_batch*_key.csv"):
        done |= set(pd.read_csv(p).doc_id)
    pool = s[~s.doc_id.isin(done)]
    pick = pd.concat([g.sample(max(1, round(n * len(g) / len(pool))), random_state=seed)
                      for _, g in pool.groupby("stratum")])
    pick = pick.sample(n=min(n, len(pick)), random_state=seed).reset_index(drop=True)  # shuffle
    pick.insert(0, "row", range(1, len(pick) + 1))
    pick[["doc_id", "stratum", "label"]].rename(columns={"label": "silver_label"}).to_csv(key(batch), index=False)
    out = pick[["row", "doc_id", "source_name", "text_excerpt"]].copy()
    out["hand_label"] = ""
    out["notes"] = ""
    out.to_csv(sheet(batch), index=False)
    print(f"wrote {sheet(batch)} ({len(out)} rows); key (don't open): {key(batch)}")


def make_enriched(n, batch, seed):
    """Sample unlabeled relevant docs: 40% down-candidates, 25% uncertain-up, 35% random."""
    d = pd.read_parquet("data/processed/documents_scored.parquet",
                        columns=["doc_id", "source_type", "source_name", "headline", "body", "is_relevant",
                                 "yield_rule_label", "yield_rule_down_hits", "yield_p_up", "yield_p_down"])
    seen = set(pd.read_csv(LABELS).doc_id) | set(pd.read_csv(SAMPLE).doc_id)
    for p in D.glob("hand_batch*_key.csv"):
        seen |= set(pd.read_csv(p).doc_id)
    d = d[d.is_relevant & ~d.doc_id.isin(seen)].copy()
    d["text_excerpt"] = (d.headline.fillna("") + " || " + d.body.fillna("").str.slice(0, 400)) \
        .str.replace(r"\s+", " ", regex=True).str.strip(" |")
    d = d[d.text_excerpt.str.len() > 20].drop_duplicates("text_excerpt")
    strata = {
        "down_candidate": ((d.yield_rule_down_hits > 0) & (d.yield_rule_label != "up")) | d.yield_p_down.between(0.15, 0.7),
        "uncertain_up": d.yield_p_up.between(0.25, 0.65),
        "random_relevant": pd.Series(True, index=d.index),
    }
    shares = {"down_candidate": 0.40, "uncertain_up": 0.25, "random_relevant": 0.35}
    picks, taken = [], set()
    for name, share in shares.items():
        pool = d[strata[name] & ~d.doc_id.isin(taken)]
        k = round(n * share)
        half = k // 2  # news is ~15% of relevant docs; force a 50/50 source split where possible
        chosen = [pool[pool.source_type == st].sample(min(half, (pool.source_type == st).sum()), random_state=seed)
                  for st in ("news", "reddit")]
        got = pd.concat(chosen)
        if len(got) < k:  # top up from whatever is left in the pool
            rest = pool[~pool.doc_id.isin(got.doc_id)]
            got = pd.concat([got, rest.sample(min(k - len(got), len(rest)), random_state=seed)])
        picks.append(got.assign(stratum=name, stratum_pool_n=len(pool)))
        taken |= set(got.doc_id)
    pick = pd.concat(picks).sample(frac=1, random_state=seed).reset_index(drop=True)
    pick.insert(0, "row", range(1, len(pick) + 1))
    pick["silver_label"] = ""  # no silver label for new docs
    pick[["doc_id", "stratum", "stratum_pool_n", "silver_label"]].to_csv(key(batch), index=False)
    out = pick[["row", "doc_id", "source_name", "text_excerpt"]].copy()
    out["hand_label"] = ""
    out["notes"] = ""
    out.to_csv(sheet(batch), index=False)
    print(pick.groupby(["stratum", "source_type"]).size().unstack(fill_value=0))
    print(f"wrote {sheet(batch)} ({len(out)} rows); key (don't open): {key(batch)}")


def merge(batch, labeler):
    h = pd.read_csv(sheet(batch))
    h["hand_label"] = h.hand_label.astype(str).str.strip().str.lower().replace({"nan": ""}).replace(ALIASES)
    bad = h[~h.hand_label.isin(VALID)]
    if len(bad):
        raise SystemExit(f"{len(bad)} rows unlabeled/invalid (rows {list(bad.row)[:10]}...). Use up/down/neutral.")
    k = pd.read_csv(key(batch)).merge(h[["doc_id", "hand_label"]], on="doc_id")
    k["silver_label"] = k.silver_label.fillna("")
    ks = k[k.silver_label != ""]
    if len(ks):
        print(f"Agreement with silver: {(ks.hand_label == ks.silver_label).mean():.1%} (n={len(ks)})")
        print(pd.crosstab(ks.hand_label, ks.silver_label, rownames=["hand"], colnames=["silver"]))
        try:
            from sklearn.metrics import cohen_kappa_score
            print("Cohen's kappa vs silver:", round(cohen_kappa_score(ks.hand_label, ks.silver_label), 3))
        except ImportError:
            pass
    else:
        print(f"No silver labels for batch {batch}; hand label counts: {k.hand_label.value_counts().to_dict()}")
    L = pd.read_csv(LABELS)
    new = pd.DataFrame({"doc_id": k.doc_id, "label": k.hand_label, "labeler": labeler,
                        "labeled_on": date.today().isoformat()})
    L = pd.concat([L[~L.doc_id.isin(new.doc_id)], new], ignore_index=True)
    L.to_csv(LABELS, index=False)
    print(f"Updated {LABELS}: {(L.labeler == labeler).sum()} labels by {labeler}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("cmd", choices=["make", "make-enriched", "merge"])
    a.add_argument("--n", type=int, default=100)
    a.add_argument("--batch", type=int, default=1)
    a.add_argument("--seed", type=int, default=42)
    a.add_argument("--labeler", default="trew")
    a = a.parse_args()
    if a.cmd == "make":
        make(a.n, a.batch, a.seed)
    elif a.cmd == "make-enriched":
        make_enriched(a.n, a.batch, a.seed)
    else:
        merge(a.batch, a.labeler)
