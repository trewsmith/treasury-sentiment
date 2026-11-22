"""
Rule-based finance taxonomy (configs/taxonomy.yaml).

- Topic tags (week 11): multi-label macro topics from keyword / regex rules.
- Yield-direction rules (week 10, layer 2): cues for whether a text implies
  higher or lower 10y yields, independent of its positive/negative tone.
  "Treasuries rally on recession fears" → down (recession_risk + market_down),
  even though a generic sentiment model reads it as negative.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from src.utils.paths import CONFIGS_DIR

YIELD_LABELS = ("up", "down", "ambiguous", "none")


@dataclass(frozen=True)
class Category:
    name: str
    description: str
    patterns: tuple[str, ...]
    regex: re.Pattern
    direction: int = 0


def _compile(patterns: list[str]) -> re.Pattern:
    return re.compile("|".join(f"(?:{p})" for p in patterns), re.I)


def load_taxonomy(path: Path | None = None) -> dict[str, list[Category]]:
    cfg_path = path or (CONFIGS_DIR / "taxonomy.yaml")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    out: dict[str, list[Category]] = {}
    for section in ("topics", "yield_direction"):
        out[section] = [
            Category(
                name=name,
                description=spec.get("description", ""),
                patterns=tuple(spec["patterns"]),
                regex=_compile(spec["patterns"]),
                direction=int(spec.get("direction", 0)),
            )
            for name, spec in (cfg.get(section) or {}).items()
        ]
    return out


def _count(texts: pd.Series, regex: re.Pattern) -> pd.Series:
    # Python `re`, not the pandas str accessor: Arrow-backed strings use RE2,
    # which rejects the lookarounds the taxonomy relies on.
    return texts.map(
        lambda t: sum(1 for _ in regex.finditer(t)) if isinstance(t, str) else 0
    ).astype("int64")


def tag_topics(texts: pd.Series, topics: list[Category]) -> pd.DataFrame:
    """
    Boolean `topic_<name>` columns, plus `topics` ("fed|inflation", "" if none)
    and `n_topics`.
    """
    out = pd.DataFrame(index=texts.index)
    for cat in topics:
        out[f"topic_{cat.name}"] = texts.map(
            lambda t, rx=cat.regex: isinstance(t, str) and rx.search(t) is not None
        ).astype(bool)
    cols = [f"topic_{c.name}" for c in topics]
    names = [c.name for c in topics]
    flags = out[cols].to_numpy()
    out["topics"] = ["|".join(n for n, f in zip(names, row) if f) for row in flags]
    out["n_topics"] = flags.sum(axis=1).astype("int64")
    return out


def yield_rule_features(texts: pd.Series, categories: list[Category]) -> pd.DataFrame:
    """
    Rule layer for yield direction:
      yield_rule_up_hits / yield_rule_down_hits — regex matches pointing each way
      yield_rule_score — up_hits − down_hits
      yield_rule_label — up / down / ambiguous (both, tied) / none (no cue)
      yield_rule_categories — matched category names, e.g. "recession_risk|market_down"
    """
    up = pd.Series(0, index=texts.index, dtype="int64")
    down = pd.Series(0, index=texts.index, dtype="int64")
    matched = {}
    for cat in categories:
        hits = _count(texts, cat.regex)
        matched[cat.name] = hits > 0
        if cat.direction > 0:
            up += hits
        elif cat.direction < 0:
            down += hits
    score = up - down
    label = pd.Series("none", index=texts.index)
    label[(up > 0) | (down > 0)] = "ambiguous"
    label[score > 0] = "up"
    label[score < 0] = "down"

    names = list(matched)
    flags = pd.DataFrame(matched).to_numpy() if names else None
    cats = (
        ["|".join(n for n, f in zip(names, row) if f) for row in flags]
        if names
        else [""] * len(texts)
    )
    return pd.DataFrame(
        {
            "yield_rule_up_hits": up,
            "yield_rule_down_hits": down,
            "yield_rule_score": score,
            "yield_rule_label": label,
            "yield_rule_categories": cats,
        },
        index=texts.index,
    )


def relevance_mask(
    source_type: pd.Series, topics: pd.DataFrame, rules: pd.DataFrame
) -> pd.Series:
    """
    Documents worth scoring with the (slow) transformer models: all news, plus
    Reddit posts that carry a macro topic tag or a yield-direction cue.
    """
    return (
        (source_type == "news")
        | (topics["n_topics"] > 0)
        | (rules["yield_rule_label"] != "none")
    )
