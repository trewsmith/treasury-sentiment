"""
Layer 1: raw text tone from three sentiment models.

  A  vader       — lexicon baseline (vaderSentiment), every document
  B  distilbert  — generic transformer (distilbert-base-uncased-finetuned-sst-2-english)
  C  finbert     — finance transformer (ProsusAI/finbert)

B and C are scored by src/nlp/transformer_scoring.py in the separate ML
environment (.venv-ml, PyTorch) and cached per text_hash in
data/interim/sentiment/<model>.parquet; this module merges those caches.

Per model the output columns are
  <m>_p_positive, <m>_p_neutral, <m>_p_negative,
  <m>_sentiment_score (= p_positive − p_negative),
  <m>_confidence (= max class probability),
  <m>_entropy (normalized to [0, 1] over the model's classes; 1 = maximally unsure)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.paths import SENTIMENT_CACHE_DIR

PROB_COLUMNS = ("p_positive", "p_neutral", "p_negative")

# Number of classes each model actually predicts (DistilBERT SST-2 has no neutral class)
MODEL_CLASSES = {"vader": 3, "distilbert": 2, "finbert": 3}
TRANSFORMER_MODELS = ("finbert", "distilbert")


def derive_scores(probs: pd.DataFrame, prefix: str, n_classes: int) -> pd.DataFrame:
    """Add sentiment_score / confidence / entropy to p_positive/p_neutral/p_negative columns."""
    p = probs[list(PROB_COLUMNS)].to_numpy(dtype="float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -np.nansum(np.where(p > 0, p * np.log(p), 0.0), axis=1) / np.log(n_classes)
    missing = np.isnan(p).any(axis=1)
    out = pd.DataFrame(index=probs.index)
    for col in PROB_COLUMNS:
        out[f"{prefix}_{col}"] = probs[col].astype("float64")
    out[f"{prefix}_sentiment_score"] = probs["p_positive"] - probs["p_negative"]
    conf = np.nanmax(np.where(missing[:, None], 0.0, p), axis=1)
    out[f"{prefix}_confidence"] = np.where(missing, np.nan, conf)
    out[f"{prefix}_entropy"] = np.where(missing, np.nan, ent)
    return out


def score_vader(texts: pd.Series) -> pd.DataFrame:
    """
    VADER lexicon scores. p_* are VADER's pos/neu/neg proportions (share of
    text that is positive/neutral/negative, summing to 1), not calibrated
    probabilities; `vader_compound` keeps VADER's own [-1, 1] summary.
    """
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()
    rows = [analyzer.polarity_scores(t if isinstance(t, str) else "") for t in texts]
    probs = pd.DataFrame(
        {
            "p_positive": [r["pos"] for r in rows],
            "p_neutral": [r["neu"] for r in rows],
            "p_negative": [r["neg"] for r in rows],
        },
        index=texts.index,
    )
    out = derive_scores(probs, "vader", MODEL_CLASSES["vader"])
    out["vader_compound"] = [r["compound"] for r in rows]
    return out


def load_transformer_scores(docs: pd.DataFrame, model: str) -> pd.DataFrame:
    """
    Join cached transformer probabilities onto docs by text_hash. Documents
    that were not scored (outside the relevance filter) get NaN.
    """
    path = SENTIMENT_CACHE_DIR / f"{model}.parquet"
    if not path.exists():
        print(f"[sentiment] no cache for {model} at {path}; columns left null")
        probs = pd.DataFrame(np.nan, index=docs.index, columns=list(PROB_COLUMNS))
    else:
        cache = pd.read_parquet(path).drop_duplicates("text_hash").set_index("text_hash")
        probs = cache.reindex(docs["text_hash"])[list(PROB_COLUMNS)]
        probs.index = docs.index
    return derive_scores(probs, model, MODEL_CLASSES[model])
