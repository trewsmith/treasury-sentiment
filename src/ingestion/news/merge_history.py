"""
Rebuild news_raw.parquet as the union of everything ever collected, so refreshes cannot lose articles.

Union of: the current file, snapshots in data/raw/news/, committed versions of news_raw.parquet
(git history), and the cached GDELT backfill. Then the normal dedupe, with labeled articles protected.
Also writes data/labels/label_texts.parquet (text of every labeled document), so labels stay usable
even if a document later leaves the corpus.

Usage: PYTHONPATH=. python src/ingestion/news/merge_history.py
"""
from __future__ import annotations

import io
import subprocess

import pandas as pd

from src.cleaning.documents import news_to_documents
from src.ingestion.news.dedupe import dedupe_articles
from src.ingestion.news.gdelt_backfill import load_cached
from src.ingestion.news.pipeline import save_news_raw
from src.utils.paths import DOCUMENTS_CLEAN_PARQUET, LABELS_DIR, NEWS_RAW_DIR, NEWS_RAW_PARQUET, PROJECT_ROOT

REL = "data/processed/news_raw.parquet"


def git_versions() -> list[pd.DataFrame]:
    try:
        shas = subprocess.check_output(["git", "log", "--format=%h", "--", REL], cwd=PROJECT_ROOT, text=True).split()
        return [pd.read_parquet(io.BytesIO(subprocess.check_output(["git", "show", f"{s}:{REL}"], cwd=PROJECT_ROOT))) for s in shas]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def main() -> None:
    parts = [pd.read_parquet(NEWS_RAW_PARQUET)] if NEWS_RAW_PARQUET.exists() else []
    parts += [pd.read_parquet(p) for p in sorted(NEWS_RAW_DIR.glob("news_raw_*.parquet"))]
    parts += git_versions()
    gd = load_cached()
    print(f"stored versions: {len(parts)}; GDELT backfill rows: {len(gd):,}")
    union = pd.concat([p for p in [*parts, gd] if len(p)], ignore_index=True)
    labels = pd.read_csv(LABELS_DIR / "yield_direction_labels.csv")
    ids = set(labels.doc_id[labels.doc_id.str.startswith("news:")].str.removeprefix("news:"))

    lab_rows = union[union.article_id.isin(ids)].sort_values("collected_at_utc").drop_duplicates("article_id", keep="first")
    out = dedupe_articles(union)
    out = pd.concat([out, lab_rows[~lab_rows.article_id.isin(out.article_id)]], ignore_index=True)
    save_news_raw(out[[c for c in lab_rows.columns]])
    print(f"news_raw: {len(out):,} articles")
    print(out.source.value_counts().head(12).to_string())

    txt = [news_to_documents(lab_rows)[["doc_id", "text", "source_type"]]]
    path = LABELS_DIR / "label_texts.parquet"
    if path.exists():
        txt.append(pd.read_parquet(path))
    if DOCUMENTS_CLEAN_PARQUET.exists():
        d = pd.read_parquet(DOCUMENTS_CLEAN_PARQUET, columns=["doc_id", "text", "source_type"])
        txt.insert(0, d[d.doc_id.isin(labels.doc_id)])
    t = pd.concat(txt, ignore_index=True).drop_duplicates("doc_id")
    t.to_parquet(path, index=False)
    print(f"label texts: {len(t):,} of {len(labels):,} labels")


if __name__ == "__main__":
    main()
