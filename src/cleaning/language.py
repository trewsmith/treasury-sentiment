"""
Lightweight, deterministic English filter.

Uses two signals, no model download:
  1. Script: share of alphabetic characters that are Latin.
  2. Function words: English stopword hits vs. common Spanish / Portuguese /
     French / German / Italian / Dutch stopwords.

Short ticker-speak ("NVDA calls?") has no reliable signal and is treated as
English unless it is mostly non-Latin script. Ambiguous cases default to English
because every configured source is an English-language outlet or subreddit.
"""

from __future__ import annotations

import re
import unicodedata

EN_STOPWORDS = frozenset(
    """
    the a an and or but if of to in on at by for with from as is are was were be been
    being this that these those it its i you he she we they me my your our their his her
    not no do does did have has had will would should could can may might must shall
    what which who whom when where why how all any some more most than then there here
    so just about into over after before up down out off again very also only own same
    """.split()
)

FOREIGN_STOPWORDS = {
    "es": frozenset("el la los las del que y en por para con una un es se lo más pero como sus al".split()),
    "pt": frozenset("o os da do das dos que e em para com uma um não mais mas como seu sua ao pelo".split()),
    "fr": frozenset("le la les des du et est une un pour dans que qui sur pas plus avec au aux ce".split()),
    "de": frozenset("der die das und ist nicht ein eine mit den dem zu auf für von sich auch im".split()),
    "it": frozenset("il lo gli della che di per con una non più anche come sono nel alla questo".split()),
    "nl": frozenset("de het een en van is dat niet op voor met zijn ook naar maar dit wordt".split()),
}

_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def latin_share(text: str) -> float:
    if text.isascii():
        return 1.0
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 1.0
    latin = sum(1 for ch in letters if ch.isascii() or "LATIN" in unicodedata.name(ch, ""))
    return latin / len(letters)


def detect_language(text: str, *, min_latin_share: float = 0.6, min_foreign_hits: int = 3) -> str:
    """
    Return 'en', a foreign code from FOREIGN_STOPWORDS, or 'non_latin'.

    A foreign label needs at least `min_foreign_hits` foreign stopwords and more
    than twice the English stopword count, so English text quoting a foreign
    name ("Bank für Arbeit und Wirtschaft") stays English.
    """
    if latin_share(text) < min_latin_share:
        return "non_latin"
    # Single letters are skipped: tickers / tenors ("10Y", "3M") look like Spanish "y"
    words = [w.lower() for w in _WORD.findall(text) if len(w) > 1]
    if not words:
        return "en"
    en_hits = sum(w in EN_STOPWORDS for w in words)
    best_lang, best_hits = "en", 0
    for lang, stops in FOREIGN_STOPWORDS.items():
        # Words shared with English ('a', 'in', 'is', 'die', …) count for neither side
        hits = sum(w in stops and w not in EN_STOPWORDS for w in words)
        if hits > best_hits:
            best_lang, best_hits = lang, hits
    if best_hits >= min_foreign_hits and best_hits > 2 * en_hits:
        return best_lang
    return "en"


def is_english(text: str, **kwargs) -> bool:
    return detect_language(text, **kwargs) == "en"
