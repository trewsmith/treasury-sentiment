"""
Layer 2 (learned): yield-direction classifier.

Trained on labeled documents in data/labels/ (doc_id, label ∈ up/down/neutral).
The current label file is SILVER (LLM-labeled, see docs/label_taxonomy.md), not
human gold; replace or extend it with hand labels and re-run the pipeline.

Model: TF-IDF (word 1–2 grams) on the first 500 chars of `text` + the rule layer's up/down hit counts
→ multinomial logistic regression (class-balanced). Evaluated with stratified
5-fold cross-validation against the rules-only baseline on the same labels.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from src.utils.paths import LABELS_DIR

LABELS = ("up", "down", "neutral")
LABEL_FILE = LABELS_DIR / "yield_direction_labels.csv"
RULE_FEATURES = ["yield_rule_up_hits", "yield_rule_down_hits"]
MAX_CHARS = 500  # headline + lead; beats 2000 on hand-label holdout (see reports/tables/yield_direction_eval.csv)


def load_labels(path: Path = LABEL_FILE) -> pd.DataFrame | None:
    if not path.exists():
        return None
    labels = pd.read_csv(path, dtype={"doc_id": str, "label": str})
    labels["label"] = labels["label"].str.strip().str.lower()
    bad = ~labels["label"].isin(LABELS)
    if bad.any():
        raise ValueError(f"{int(bad.sum())} rows in {path} have labels outside {LABELS}")
    return labels.drop_duplicates("doc_id", keep="last")


def _truncate(x, max_chars: int = MAX_CHARS):
    return pd.Series(x).fillna("").str.slice(0, max_chars).tolist()


def build_model(
    C: float = 4.0, max_chars: int = MAX_CHARS, extra_features: list[str] | None = None
) -> Pipeline:
    """TF-IDF + rule hits (+ optional dense columns, e.g. FinBERT scores) → balanced LR."""
    transformers = [
        (
            "text",
            Pipeline(
                [
                    ("trunc", FunctionTransformer(partial(_truncate, max_chars=max_chars))),
                    (
                        "tfidf",
                        TfidfVectorizer(
                            ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=50_000
                        ),
                    ),
                ]
            ),
            "text",
        ),
        ("rules", FunctionTransformer(np.log1p), RULE_FEATURES),
    ]
    if extra_features:
        transformers.append(("extra", "passthrough", extra_features))
    clf = LogisticRegression(C=C, class_weight="balanced", max_iter=5000)
    return Pipeline([("features", ColumnTransformer(transformers)), ("clf", clf)])


def rule_baseline(rule_label: pd.Series) -> pd.Series:
    """Rules-only prediction: up/down as-is, ambiguous/none → neutral."""
    return rule_label.where(rule_label.isin(["up", "down"]), "neutral")


@dataclass
class EvalResult:
    n: int
    label_counts: dict[str, int]
    model_macro_f1: float
    rule_macro_f1: float
    model_report: str
    rule_report: str
    model_confusion: pd.DataFrame


def evaluate(train: pd.DataFrame, *, folds: int = 5, seed: int = 0) -> EvalResult:
    """Cross-validated comparison of the classifier vs. the rules on labeled docs."""
    y = train["label"]
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    pred = cross_val_predict(build_model(), train[["text"] + RULE_FEATURES], y, cv=cv)
    rule_pred = rule_baseline(train["yield_rule_label"])
    labels = list(LABELS)
    return EvalResult(
        n=len(train),
        label_counts=y.value_counts().to_dict(),
        model_macro_f1=f1_score(y, pred, average="macro"),
        rule_macro_f1=f1_score(y, rule_pred, average="macro"),
        model_report=classification_report(y, pred, labels=labels, digits=3, zero_division=0),
        rule_report=classification_report(y, rule_pred, labels=labels, digits=3, zero_division=0),
        model_confusion=pd.DataFrame(
            confusion_matrix(y, pred, labels=labels),
            index=[f"true_{x}" for x in labels],
            columns=[f"pred_{x}" for x in labels],
        ),
    )


def fit_predict(train: pd.DataFrame, docs: pd.DataFrame) -> tuple[Pipeline, pd.DataFrame]:
    """Fit on all labeled docs; return p_up / p_down / p_neutral for every doc."""
    model = build_model().fit(train[["text"] + RULE_FEATURES], train["label"])
    proba = model.predict_proba(docs[["text"] + RULE_FEATURES])
    classes = list(model.classes_)
    out = pd.DataFrame(index=docs.index)
    for lab in LABELS:
        out[f"yield_p_{lab}"] = proba[:, classes.index(lab)] if lab in classes else 0.0
    return model, out
