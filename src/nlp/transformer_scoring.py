"""
Score documents with transformer sentiment models (runs in the ML environment).

This machine's main venv (Python 3.14, Intel macOS) cannot install PyTorch, so
this script runs in .venv-ml (Python 3.12 + torch 2.2, see README). It only
needs pandas / pyarrow / pyyaml / torch / transformers.

Only relevant documents are scored (news + docs with a macro topic or a
yield-direction cue, see src.nlp.taxonomy.relevance_mask) to keep CPU time
manageable. Results are cached per unique text_hash in
data/interim/sentiment/<model>.parquet and appended in chunks, so an
interrupted run resumes where it stopped.

Usage:
  PYTHONPATH=. .venv-ml/bin/python src/nlp/transformer_scoring.py --model finbert
  PYTHONPATH=. .venv-ml/bin/python src/nlp/transformer_scoring.py --model distilbert
  PYTHONPATH=. .venv-ml/bin/python src/nlp/transformer_scoring.py --model finbert --limit 500  # smoke test
"""

from __future__ import annotations

import argparse
import time

import pandas as pd

from src.nlp.taxonomy import load_taxonomy, relevance_mask, tag_topics, yield_rule_features
from src.utils.paths import DOCUMENTS_CLEAN_PARQUET, SENTIMENT_CACHE_DIR

MODELS = {
    "finbert": "ProsusAI/finbert",
    "distilbert": "distilbert-base-uncased-finetuned-sst-2-english",
}
MAX_TOKENS = 128


def _label_map(id2label: dict[int, str]) -> dict[int, str]:
    """Map model label ids to p_positive / p_neutral / p_negative."""
    out = {}
    for idx, name in id2label.items():
        name = name.lower()
        if name.startswith("pos"):
            out[idx] = "p_positive"
        elif name.startswith("neg"):
            out[idx] = "p_negative"
        elif name.startswith("neu"):
            out[idx] = "p_neutral"
        else:
            raise ValueError(f"Unexpected label {name!r}")
    return out


def texts_to_score(limit: int | None = None) -> pd.DataFrame:
    docs = pd.read_parquet(DOCUMENTS_CLEAN_PARQUET, columns=["text", "text_hash", "source_type"])
    tax = load_taxonomy()
    topics = tag_topics(docs["text"], tax["topics"])
    rules = yield_rule_features(docs["text"], tax["yield_direction"])
    keep = relevance_mask(docs["source_type"], topics, rules)
    todo = docs.loc[keep, ["text_hash", "text"]].drop_duplicates("text_hash")
    print(f"relevant docs: {int(keep.sum()):,} / {len(docs):,} ({todo.shape[0]:,} unique texts)")
    return todo.head(limit) if limit else todo


def score(model_key: str, *, batch_size: int = 32, chunk_size: int = 2000, limit: int | None = None):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.set_num_threads(max(1, torch.get_num_threads()))
    name = MODELS[model_key]
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name).eval()
    labels = _label_map(model.config.id2label)

    SENTIMENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    part_dir = SENTIMENT_CACHE_DIR / f"{model_key}_parts"
    part_dir.mkdir(exist_ok=True)
    done = set()
    for part in part_dir.glob("*.parquet"):
        done.update(pd.read_parquet(part, columns=["text_hash"])["text_hash"])

    todo = texts_to_score(limit)
    todo = todo[~todo["text_hash"].isin(done)]
    print(f"{model_key}: {len(done):,} cached, {len(todo):,} to score")

    start = time.time()
    n_parts = len(list(part_dir.glob("*.parquet")))
    for c0 in range(0, len(todo), chunk_size):
        chunk = todo.iloc[c0 : c0 + chunk_size]
        rows = []
        for b0 in range(0, len(chunk), batch_size):
            batch = chunk.iloc[b0 : b0 + batch_size]
            enc = tok(
                batch["text"].tolist(),
                truncation=True,
                max_length=MAX_TOKENS,
                padding=True,
                return_tensors="pt",
            )
            with torch.inference_mode():
                probs = torch.softmax(model(**enc).logits, dim=-1).numpy()
            for h, p in zip(batch["text_hash"], probs):
                row = {"text_hash": h, "p_positive": 0.0, "p_neutral": 0.0, "p_negative": 0.0}
                for idx, col in labels.items():
                    row[col] = float(p[idx])
                rows.append(row)
        pd.DataFrame(rows).to_parquet(part_dir / f"part-{n_parts:05d}.parquet", index=False)
        n_parts += 1
        done_n = c0 + len(chunk)
        rate = done_n / (time.time() - start)
        eta = (len(todo) - done_n) / rate / 60 if rate else float("nan")
        print(f"  {done_n:,}/{len(todo):,} ({rate:.1f} texts/s, ~{eta:.0f} min left)", flush=True)

    parts = [pd.read_parquet(p) for p in sorted(part_dir.glob("*.parquet"))]
    if parts:
        merged = pd.concat(parts, ignore_index=True).drop_duplicates("text_hash")
        merged["model"] = name
        merged.to_parquet(SENTIMENT_CACHE_DIR / f"{model_key}.parquet", index=False)
        print(f"Wrote {SENTIMENT_CACHE_DIR / f'{model_key}.parquet'} ({len(merged):,} texts)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transformer sentiment scoring (ML venv)")
    parser.add_argument("--model", choices=sorted(MODELS), required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--limit", type=int, default=None, help="Score only the first N texts")
    args = parser.parse_args()
    score(args.model, batch_size=args.batch_size, limit=args.limit)


if __name__ == "__main__":
    main()
