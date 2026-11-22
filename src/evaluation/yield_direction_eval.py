"""Evaluate the yield-direction classifier against hand labels.

Protocol
  * Gold test set  = rows in data/labels/yield_direction_labels.csv labeled by a human
                     (labeler != 'claude-silver'). Never used for training in the holdout run.
  * Holdout run    = train on silver labels only, score the hand labels.
  * CV run         = stratified repeated 5-fold on silver + hand together (less noisy, but the
                     hand labels are only ~10% of the folds).
Models compared: rules only, current LR (TF-IDF + rule hits), shorter text window,
C sweep, and + FinBERT scores.

Usage:  PYTHONPATH=. python src/evaluation/yield_direction_eval.py
Output: reports/tables/yield_direction_eval.csv, reports/tables/yield_direction_holdout_predictions.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, cohen_kappa_score, confusion_matrix, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold

from src.nlp import yield_classifier as yc
from src.utils.paths import PROCESSED_DIR, PROJECT_ROOT

SILVER = "claude-silver"
FINBERT = ["finbert_p_positive", "finbert_p_negative", "finbert_sentiment_score"]
TABLES = PROJECT_ROOT / "reports" / "tables"

MODELS = {
    "rules_only": None,
    "lr 500ch (default)": dict(),
    "lr 2000ch (old default)": dict(max_chars=2000),
    "lr 300ch": dict(max_chars=300),
    "lr C=1": dict(C=1.0),
    "lr C=16": dict(C=16.0),
    "lr 500ch + finbert": dict(extra_features=FINBERT),
}


def load() -> pd.DataFrame:
    docs = pd.read_parquet(PROCESSED_DIR / "documents_scored.parquet")
    keep = ["doc_id", "source_type", "text", *yc.RULE_FEATURES, "yield_rule_label", *FINBERT]
    labels = yc.load_labels()
    df = labels.merge(docs[keep], on="doc_id", how="inner")
    df[FINBERT] = df[FINBERT].fillna(0.0)  # FinBERT only scored relevant docs
    df["is_gold"] = df["labeler"] != SILVER
    return df.reset_index(drop=True)


def predict(name: str, cfg, train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    if cfg is None:
        return yc.rule_baseline(test["yield_rule_label"]).to_numpy()
    cols = ["text", *yc.RULE_FEATURES, *cfg.get("extra_features", [])]
    model = yc.build_model(**cfg).fit(train[cols], train["label"])
    return model.predict(test[cols])


def boot_ci(y, p, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    f = [f1_score(y[i], p[i], average="macro") for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return np.percentile(f, [2.5, 97.5])


def holdout_metrics(name, cfg, train, test):
    p = predict(name, cfg, train, test)
    lo, hi = boot_ci(test.label, p)
    return p, dict(
        macro_f1=f1_score(test.label, p, average="macro"), ci_lo=lo, ci_hi=hi,
        acc=(test.label.to_numpy() == p).mean(), kappa=cohen_kappa_score(test.label, p),
        down_f1=f1_score(test.label, p, labels=["down"], average=None, zero_division=0)[0],
    )


def main() -> None:
    df = load()
    gold, silver = df[df.is_gold], df[~df.is_gold]
    b2_ids = set(pd.read_csv(PROJECT_ROOT / "data/labels/hand_batch2_key.csv").doc_id)
    b2 = df[df.doc_id.isin(b2_ids)]  # enriched sample (down/uncertain oversampled): NOT base-rate representative
    b1 = gold[~gold.doc_id.isin(b2_ids)]
    print(f"labels {len(df)}: silver {len(silver)}, hand {len(gold)} (batch1 {len(b1)}, batch2 {len(b2)})")
    print(f"hand dist {gold.label.value_counts().to_dict()}; batch2 {b2.label.value_counts().to_dict()}")
    rows = []
    preds = gold[["doc_id", "label"]].rename(columns={"label": "hand_label"}).copy()
    rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=0)
    for name, cfg in MODELS.items():
        # A: train silver -> test all hand labels.  B: train silver+batch1 -> test batch2 (clean for later rule edits)
        pA, mA = holdout_metrics(name, cfg, silver, gold)
        pB, mB = holdout_metrics(name, cfg, pd.concat([silver, b1]), b2)
        preds[name] = pA
        cv = []
        for tr, te in rskf.split(df, df.label):
            cv.append(f1_score(df.label.iloc[te], predict(name, cfg, df.iloc[tr], df.iloc[te]), average="macro"))
        row = {"model": name, "cv_macro_f1": np.mean(cv)}
        row.update({f"A_hand_{k}": v for k, v in mA.items()})
        row.update({f"B_batch2_{k}": v for k, v in mB.items()})
        rows.append(row)
        print(f"{name:26s} A(hand,n={len(gold)}) F1 {mA['macro_f1']:.3f} [{mA['ci_lo']:.2f},{mA['ci_hi']:.2f}] down-F1 {mA['down_f1']:.2f} | "
              f"B(batch2,n={len(b2)}) F1 {mB['macro_f1']:.3f} acc {mB['acc']:.2f} down-F1 {mB['down_f1']:.2f} | CV {np.mean(cv):.3f}")
    res = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    res.to_csv(TABLES / "yield_direction_eval.csv", index=False)
    preds.to_csv(TABLES / "yield_direction_holdout_predictions.csv", index=False)
    cur = "lr 500ch (default)"
    print("\nPer-class report (A, current model):")
    print(classification_report(gold.label, preds[cur], labels=list(yc.LABELS), digits=3, zero_division=0))
    print(pd.DataFrame(confusion_matrix(gold.label, preds[cur], labels=list(yc.LABELS)),
                       index=[f"true_{x}" for x in yc.LABELS], columns=[f"pred_{x}" for x in yc.LABELS]))
    print("\nBest by CV macro-F1:", res.iloc[1:].sort_values("cv_macro_f1").iloc[-1].model)


if __name__ == "__main__":
    main()
