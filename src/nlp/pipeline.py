"""
Score documents_clean.parquet → documents_scored.parquet (weeks 9–11).

Layers added per document:
  - topic tags (week 11)                          topic_*, topics, n_topics
  - relevance flag (transformer scoring scope)    is_relevant
  - raw sentiment, 3 models (week 9)              vader_*, distilbert_*, finbert_*
  - yield-direction rules + classifier (week 10)  yield_rule_*, yield_p_*, yield_direction_*

Also writes the week 11 topic tables / figure and the label taxonomy doc.

Usage:
  PYTHONPATH=. python src/nlp/pipeline.py
  PYTHONPATH=. python src/nlp/pipeline.py --export-label-sample 1000   # labeling sheet

Transformer scores come from src/nlp/transformer_scoring.py (run in .venv-ml
first); without its caches the distilbert_* / finbert_* columns are null.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml

from src.nlp import yield_classifier as yc
from src.nlp.sentiment import TRANSFORMER_MODELS, load_transformer_scores, score_vader
from src.nlp.taxonomy import (
    load_taxonomy,
    relevance_mask,
    tag_topics,
    yield_rule_features,
)
from src.utils.paths import (
    CONFIGS_DIR,
    DOCS_DIR,
    DOCUMENTS_CLEAN_PARQUET,
    DOCUMENTS_SCORED_PARQUET,
    FIGURES_DIR,
    LABELS_DIR,
    MODELS_DIR,
    TABLES_DIR,
    ensure_data_dirs,
)

LABEL_SAMPLE_PATH = LABELS_DIR / "yield_direction_sample.csv"
TAXONOMY_DOC_PATH = DOCS_DIR / "label_taxonomy.md"


def score_documents(docs: pd.DataFrame) -> tuple[pd.DataFrame, yc.EvalResult | None]:
    tax = load_taxonomy()
    print("Tagging topics + yield rules …")
    topics = tag_topics(docs["text"], tax["topics"])
    rules = yield_rule_features(docs["text"], tax["yield_direction"])
    out = pd.concat([docs, topics, rules], axis=1)
    out["is_relevant"] = relevance_mask(out["source_type"], topics, rules)

    print("VADER …")
    parts = [score_vader(out["text"])]
    for model in TRANSFORMER_MODELS:
        parts.append(load_transformer_scores(out, model))
    out = pd.concat([out] + parts, axis=1)

    labels = yc.load_labels()
    evaluation = None
    if labels is not None:
        train = yc.label_frame(out, labels[["doc_id", "label"]])
        missing = len(labels) - len(train)
        if missing:
            print(f"[yield] {missing} labeled doc_ids not in the corpus (ignored)")
        print(f"Yield classifier: {len(train):,} labeled docs, 5-fold CV …")
        evaluation = yc.evaluate(train)
        print(f"  macro-F1 classifier {evaluation.model_macro_f1:.3f} vs rules {evaluation.rule_macro_f1:.3f}")
        model, proba = yc.fit_predict(train, out)
        joblib.dump(model, MODELS_DIR / "yield_direction_lr.joblib")
        out = pd.concat([out, proba], axis=1)
        p = out[[f"yield_p_{lab}" for lab in yc.LABELS]].to_numpy()
        out["yield_direction_label"] = np.array(yc.LABELS)[p.argmax(axis=1)]
        out["yield_direction_signal"] = out["yield_p_up"] - out["yield_p_down"]
        out["yield_direction_source"] = "classifier"
    else:
        print("[yield] no label file; yield_direction_signal falls back to the rules")
        for lab in yc.LABELS:
            out[f"yield_p_{lab}"] = np.nan
        out["yield_direction_label"] = yc.rule_baseline(out["yield_rule_label"])
        out["yield_direction_signal"] = np.sign(out["yield_rule_score"]).astype("float64")
        out["yield_direction_source"] = "rules"
    return out, evaluation


# ---------------------------------------------------------------------------
# Week 11 deliverables: topic counts over time, topic-specific sentiment
# ---------------------------------------------------------------------------


def _topic_long(scored: pd.DataFrame, topic_names: list[str]) -> pd.DataFrame:
    month = scored["timestamp_et"].dt.strftime("%Y-%m")
    frames = []
    for t in topic_names:
        sub = scored[scored[f"topic_{t}"]]
        frames.append(
            pd.DataFrame(
                {
                    "month": month[sub.index],
                    "source_type": sub["source_type"],
                    "topic": t,
                    "finbert_sentiment_score": sub["finbert_sentiment_score"],
                    "vader_sentiment_score": sub["vader_sentiment_score"],
                    "yield_direction_signal": sub["yield_direction_signal"],
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def write_topic_tables(scored: pd.DataFrame, topic_names: list[str]) -> list[Path]:
    long = _topic_long(scored, topic_names)
    month = scored["timestamp_et"].dt.strftime("%Y-%m")
    totals = scored.groupby([month.rename("month"), "source_type"]).size().rename("docs_total")

    counts = long.groupby(["month", "source_type", "topic"]).size().rename("docs").reset_index()
    counts = counts.merge(totals.reset_index(), on=["month", "source_type"])
    counts["share"] = (counts["docs"] / counts["docs_total"]).round(4)
    counts_path = TABLES_DIR / "topic_counts_monthly.csv"
    counts.to_csv(counts_path, index=False)

    agg = (
        long.groupby(["month", "source_type", "topic"])
        .agg(
            docs=("topic", "size"),
            finbert_scored=("finbert_sentiment_score", "count"),
            finbert_mean=("finbert_sentiment_score", "mean"),
            vader_mean=("vader_sentiment_score", "mean"),
            yield_signal_mean=("yield_direction_signal", "mean"),
        )
        .round(4)
        .reset_index()
    )
    sent_path = TABLES_DIR / "topic_sentiment_monthly.csv"
    agg.to_csv(sent_path, index=False)

    overall = (
        long.groupby(["source_type", "topic"])
        .agg(
            docs=("topic", "size"),
            finbert_mean=("finbert_sentiment_score", "mean"),
            vader_mean=("vader_sentiment_score", "mean"),
            yield_signal_mean=("yield_direction_signal", "mean"),
        )
        .round(4)
        .reset_index()
    )
    overall_path = TABLES_DIR / "topic_sentiment_overall.csv"
    overall.to_csv(overall_path, index=False)
    return [counts_path, sent_path, overall_path]


def plot_topic_shares(counts_csv: Path, topic_names: list[str], *, months: int = 22) -> Path:
    """Small multiples: monthly share of each source's docs tagged with each topic."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, muted, grid, base, surface = "#0b0b0b", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
    colors = {"news": "#2a78d6", "reddit": "#eb6834"}  # validated categorical slots 1–2

    counts = pd.read_csv(counts_csv)
    keep = sorted(counts["month"].unique())[-months:]
    counts = counts[counts["month"].isin(keep)]
    x = {m: i for i, m in enumerate(keep)}

    ncols = 4
    nrows = int(np.ceil(len(topic_names) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.1 * nrows), sharex=True, sharey=True)
    fig.patch.set_facecolor(surface)
    ymax = 0.0
    for ax, topic in zip(axes.flat, topic_names):
        ax.set_facecolor(surface)
        for st, color in colors.items():
            s = counts[(counts["topic"] == topic) & (counts["source_type"] == st)]
            s = s.set_index("month").reindex(keep)["share"].fillna(0) * 100
            ymax = max(ymax, s.max())
            ax.plot([x[m] for m in keep], s.values, color=color, lw=2, label=st)
            ax.annotate(  # direct label at line end
                st, (len(keep) - 1, s.values[-1]), xytext=(4, 0), textcoords="offset points",
                color="#52514e", fontsize=8, va="center",
            )
        ax.set_title(topic.replace("_", " "), loc="left", fontsize=10, color=ink)
        ax.grid(axis="y", color=grid, lw=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(base)
        ax.tick_params(colors=muted, labelsize=8)
    for ax in list(axes.flat)[len(topic_names):]:
        ax.set_visible(False)
    ticks = list(range(0, len(keep), 3))
    for ax in axes.flat:
        ax.set_xticks(ticks)
        ax.set_xticklabels([keep[i] for i in ticks], rotation=45, ha="right")
        ax.set_xlim(-0.5, len(keep) + 2.5)
    axes.flat[0].set_ylim(0, ymax * 1.1 if ymax else 1)
    for row in axes:
        row[0].set_ylabel("% of docs", color=muted, fontsize=9)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", frameon=False, fontsize=9, ncols=2)
    fig.suptitle(
        "Share of documents tagged with each macro topic, by month (ET)",
        x=0.01, ha="left", fontsize=12, color=ink,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = FIGURES_DIR / "topic_shares_monthly.png"
    fig.savefig(path, dpi=150, facecolor=surface)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Labeling sample + taxonomy doc
# ---------------------------------------------------------------------------


def export_label_sample(scored: pd.DataFrame, n: int, seed: int = 0) -> Path:
    """
    Stratified sample for yield-direction labeling: half news / half Reddit;
    within each, rule up 30% / rule down 30% / ambiguous 10% / relevant-but-no-cue
    20% / not relevant 10%, so all classes and hard negatives are represented.
    """
    rng = np.random.default_rng(seed)
    strata = {
        "up": scored["yield_rule_label"] == "up",
        "down": scored["yield_rule_label"] == "down",
        "ambiguous": scored["yield_rule_label"] == "ambiguous",
        "topic_only": (scored["yield_rule_label"] == "none") & scored["is_relevant"],
        "irrelevant": ~scored["is_relevant"],
    }
    shares = {"up": 0.3, "down": 0.3, "ambiguous": 0.1, "topic_only": 0.2, "irrelevant": 0.1}
    picks = []
    for st in ("news", "reddit"):
        pool = scored[scored["source_type"] == st]
        for name, share in shares.items():
            cand = pool[strata[name].loc[pool.index]]
            k = min(len(cand), int(round(n / 2 * share)))
            if k:
                idx = rng.choice(cand.index.to_numpy(), size=k, replace=False)
                picks.append(scored.loc[idx].assign(stratum=name))
    sample = pd.concat(picks).sample(frac=1, random_state=seed).reset_index(drop=True)
    excerpt = (sample["headline"] + " || " + sample["body"].fillna("").str.slice(0, 400)).str.replace(
        r"\s+", " ", regex=True
    )
    out = pd.DataFrame(
        {
            "label_id": np.arange(1, len(sample) + 1),
            "doc_id": sample["doc_id"],
            "source_name": sample["source_name"],
            "stratum": sample["stratum"],
            "text_excerpt": excerpt.str.strip(" |"),
            "label": "",
        }
    )
    out.to_csv(LABEL_SAMPLE_PATH, index=False)
    return LABEL_SAMPLE_PATH


def write_taxonomy_doc(evaluation: yc.EvalResult | None) -> Path:
    with open(CONFIGS_DIR / "taxonomy.yaml") as f:
        cfg = yaml.safe_load(f)
    lines = [
        "# Label Taxonomy — Treasury Sentiment",
        "",
        "Generated by `src/nlp/pipeline.py` from `configs/taxonomy.yaml`. Edit the YAML, not this file.",
        "",
        "Documents get two independent layers:",
        "",
        "1. **Raw sentiment (tone)** — positive / neutral / negative from VADER, DistilBERT, FinBERT.",
        "2. **Yield direction** — what the text implies for the 10-year Treasury yield:",
        "   `up` (hawkish / inflationary / growth-hot / fiscal supply / yields reported rising),",
        "   `down` (dovish / disinflationary / recession risk / risk-off / yields reported falling),",
        "   `neutral` (ambiguous, offsetting, or no rates implication).",
        "",
        "The layers disagree by design: *“Treasuries rally on recession fears”* is negative in tone",
        "but `down` for yields (bullish for Treasury prices).",
        "",
        "## Layer 2: yield-direction categories",
        "",
        "| Category | Direction | Meaning | Rules |",
        "|---|---|---|---|",
    ]
    for name, spec in cfg["yield_direction"].items():
        arrow = "↑ up" if spec["direction"] > 0 else "↓ down"
        lines.append(f"| `{name}` | {arrow} | {spec['description']} | {len(spec['patterns'])} |")
    lines += [
        "",
        "**Rule scoring.** Every regex match adds its category's direction (+1 / −1).",
        "`yield_rule_score` = up matches − down matches; `yield_rule_label` is `up` / `down` by sign,",
        "`ambiguous` when cues exist but cancel, `none` when no cue matches.",
        "",
        "**Classifier.** TF-IDF (1–2 grams) + log rule-hit counts → class-balanced logistic regression,",
        "trained on `data/labels/yield_direction_labels.csv`. `yield_direction_signal` = P(up) − P(down) ∈ [−1, 1].",
        "Without a label file the signal falls back to sign(`yield_rule_score`).",
        "",
        "## Labeling guidelines (used for the silver labels)",
        "",
        "Label what the text implies for **U.S. 10-year yields**, judged from the text alone:",
        "",
        "- **up** — hawkish Fed signals (hikes, fewer/later cuts, QT); hot inflation or inflation",
        "  fears; strong jobs/GDP/spending; bigger deficits or Treasury supply, weak auctions,",
        "  U.S. downgrades; reports that yields rose / Treasuries sold off.",
        "- **down** — dovish Fed signals (cuts, pauses, QE); cooling inflation; weak data, layoffs,",
        "  recession fears; equity crashes, crises, flight to safety; reports that yields fell /",
        "  Treasuries rallied.",
        "- **neutral** — no rates implication (single-stock talk, personal finance, memes,",
        "  bank enforcement notices), or cues that clearly offset each other.",
        "- Non-U.S. rates news counts only if it plausibly moves U.S. yields (e.g. a global bond rout).",
        "- Questions (“Will the Fed cut?”) are labeled by the premise they push, if any; pure",
        "  questions with no stance are neutral.",
        "",
        "## Layer 1 complement: macro topics (week 11)",
        "",
        "| Topic | Covers | Rules |",
        "|---|---|---|",
    ]
    for name, spec in cfg["topics"].items():
        lines.append(f"| `{name}` | {spec['description']} | {len(spec['patterns'])} |")
    lines += [
        "",
        "Topics are multi-label (`topic_<name>` booleans; `topics` joins them with `|`).",
        "`is_relevant` = news, or any topic, or any yield cue — the scope scored by the transformers.",
        "",
    ]
    if evaluation is not None:
        counts = ", ".join(f"{k}: {v}" for k, v in sorted(evaluation.label_counts.items()))
        lines += [
            "## Classifier evaluation (5-fold stratified CV on the label file)",
            "",
            f"- Labeled docs: {evaluation.n:,} ({counts})",
            f"- **Macro-F1 classifier: {evaluation.model_macro_f1:.3f}** vs rules-only: {evaluation.rule_macro_f1:.3f}",
            "- Labels are **silver** (LLM-assigned): metrics measure agreement with those labels, not",
            "  ground truth. Hand-check a subset before relying on them.",
            "",
            "Classifier:",
            "",
            "```",
            evaluation.model_report.rstrip(),
            "```",
            "",
            "Rules only:",
            "",
            "```",
            evaluation.rule_report.rstrip(),
            "```",
            "",
            "Confusion matrix (classifier, CV):",
            "",
            "```",
            evaluation.model_confusion.to_string(),
            "```",
            "",
        ]
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    TAXONOMY_DOC_PATH.write_text("\n".join(lines))
    return TAXONOMY_DOC_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="Score documents → documents_scored.parquet")
    parser.add_argument(
        "--export-label-sample", type=int, default=None, metavar="N",
        help="Write a stratified labeling sheet of N docs to data/labels/ and exit",
    )
    args = parser.parse_args()
    ensure_data_dirs()

    docs = pd.read_parquet(DOCUMENTS_CLEAN_PARQUET)
    print(f"Loaded {len(docs):,} documents")
    scored, evaluation = score_documents(docs)

    if args.export_label_sample:
        path = export_label_sample(scored, args.export_label_sample)
        print(f"Wrote {path}")
        return

    scored.to_parquet(DOCUMENTS_SCORED_PARQUET, index=False)
    print(f"Wrote {DOCUMENTS_SCORED_PARQUET} ({len(scored):,} docs, {scored.shape[1]} columns)")

    topic_names = [c.name for c in load_taxonomy()["topics"]]
    tables = write_topic_tables(scored, topic_names)
    fig = plot_topic_shares(tables[0], topic_names)
    doc = write_taxonomy_doc(evaluation)
    for p in [*tables, fig, doc]:
        print(f"Wrote {p}")
    rel = scored["is_relevant"]
    print(f"Relevant: {int(rel.sum()):,} ({rel.mean():.1%}); "
          f"FinBERT scored: {int(scored['finbert_p_positive'].notna().sum()):,}")
    print(scored["yield_direction_label"].value_counts())


if __name__ == "__main__":
    main()
