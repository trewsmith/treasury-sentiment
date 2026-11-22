"""Text normalization and boilerplate stripping for news and Reddit documents."""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
import warnings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Bodies that are only a removal marker carry no text
REMOVED_MARKERS = {"[removed]", "[deleted]", "[removed by reddit]", "[ removed by reddit ]"}

_HTML_TAG = re.compile(r"<\s*/?\s*[a-zA-Z][^>]*>")
_ZERO_WIDTH = re.compile(r"[​‌‍⁠﻿]")
_MD_LINK = re.compile(r"!?\[([^\]]*)\]\((?:[^()\s]|\([^()\s]*\))+\)")
_URL = re.compile(r"(?:https?://|www\.)\S+", re.I)
_MD_EMPHASIS = re.compile(r"(\*\*|__|~~|>!|!<|`{1,3})")
_MD_LINE_PREFIX = re.compile(r"^[ \t]*(?:#{1,6}[ \t]+|>[ \t]?|[-*+][ \t]+(?=\S))", re.M)
_MD_TABLE_RULE = re.compile(r"^[ \t]*\|?[ \t]*:?-{3,}:?[ \t]*(\|[ \t]*:?-{3,}:?[ \t]*)*\|?[ \t]*$", re.M)
_HRULE = re.compile(r"^[ \t]*(?:[-*_][ \t]*){3,}$", re.M)
_SPACES = re.compile(r"[ \t ]+")
_BLANK_LINES = re.compile(r"\n\s*\n+")

# Whole lines dropped as publisher / platform boilerplate (matched case-insensitively)
BOILERPLATE_LINE_PATTERNS = [
    r"for media inquiries,? (?:call|e-?mail|contact).*",
    r"for (?:immediate )?release(?: at .*)?",
    r"(?:\d+\.\s*)?the views expressed (?:here|in this .*?) are (?:my|our) own.*",
    r"return to (?:text|top)",
    r"continue reading\.*",
    r"read more\W*",
    r"click here.*",
    r"sign up (?:for|to) .*newsletter.*",
    r"(?:share|follow us) on .*",
    r"(?:edit|update)\s*:?\s*(?:typo|formatting|spelling)s?\.?",
    r"(?:last updated|accessibility statement|privacy policy|terms of (?:use|service)).*",
    # Bare dateline, e.g. Fed press releases open with "May 10, 2018"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.? \d{1,2}, \d{4}",
]
_BOILERPLATE = re.compile(
    r"^[ \t]*(?:" + "|".join(BOILERPLATE_LINE_PATTERNS) + r")[ \t]*$", re.I | re.M
)
# Inline variant for single-line bodies (e.g. Guardian RSS summaries end "… Continue reading...")
_TRAILING_BOILERPLATE = re.compile(r"\s*(?:continue reading|read more)\s*(?:\.{3}|…)?\s*$", re.I)

# Google News titles end with " - <Publisher>"
_GNEWS_PUBLISHER = re.compile(r"\s+[-–—|]\s+([^-–—|]{2,60})$")


# UTF-8 bytes mis-decoded as Latin-1: a lead byte followed by a C1 control
# (never legitimate text), e.g. "â\x80\x99" → "’". Recoverable exactly.
_LATIN1_MOJIBAKE = re.compile(r"[\u00c2-\u00f4][\u0080-\u009f][\u0080-\u00bf]?")

# Same bug after the C1 bytes were stripped upstream (Fed bodies enriched before
# the enrich.py charset fix): only a bare "â" survives, so the original
# punctuation is inferred from context. Applied to news bodies only — Reddit has
# legitimate "â" ("coup de grâce").
_BARE_A_RULES = [
    (re.compile(r"â¦"), "…"),
    (re.compile(r"(?<=\d)â(?=\d)"), "-"),  # 2023â2024
    (re.compile(r"(?<=[A-Za-z\d])â(?=[a-z])"), "'"),  # Iâs, 1990âs
    (re.compile(r"(?<=[A-Za-z\d])â(?=[A-Z\d])"), "-"),  # TreasuryâFederal
    (re.compile(r"(?<=\s)â(?=\s)"), "-"),  # growth â and
    (re.compile(r"(?:(?<=^)|(?<=[\s(\[]))â(?=\S)", re.M), '"'),  # âGlobal
    (re.compile(r"(?<=\S)â"), '"'),  # Worldâ
    (re.compile(r"â"), ""),
]


def fix_mojibake(text: str, *, bare_a: bool = False) -> str:
    def _decode(m: re.Match) -> str:
        try:
            return m.group(0).encode("latin-1").decode("utf-8")
        except UnicodeError:
            return m.group(0)

    text = _LATIN1_MOJIBAKE.sub(_decode, text)
    if bare_a and "â" in text:
        for rx, repl in _BARE_A_RULES:
            text = rx.sub(repl, text)
    return text


def is_missing(val) -> bool:
    if val is None:
        return True
    try:
        return bool(val != val)  # NaN / pd.NA-safe check without importing pandas
    except (TypeError, ValueError):
        return False


def html_to_text(text: str) -> str:
    """Strip HTML tags/entities. Plain text only gets entity unescaping."""
    if _HTML_TAG.search(text):
        soup = BeautifulSoup(text, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()
        for br in soup.find_all(["br", "p", "li", "div", "h1", "h2", "h3", "h4", "tr"]):
            br.insert_before("\n")
        text = soup.get_text(" ")
    # Reddit selftext is double-escaped in places (&amp;#x200B;)
    for _ in range(2):
        text = html.unescape(text)
    return text


def strip_markdown(text: str) -> str:
    text = _MD_LINK.sub(r"\1", text)
    text = _URL.sub(" ", text)
    text = _MD_TABLE_RULE.sub("", text)
    text = _HRULE.sub("", text)
    text = _MD_LINE_PREFIX.sub("", text)
    text = _MD_EMPHASIS.sub("", text)
    text = text.replace("|", " ")
    return text


def normalize_whitespace(text: str) -> str:
    text = _SPACES.sub(" ", text)
    lines = [ln.strip() for ln in text.split("\n")]
    text = "\n".join(lines)
    return _BLANK_LINES.sub("\n\n", text).strip()


def clean_text(val, *, markdown: bool = False, repair_bare_a: bool = False) -> str:
    """
    Normalize one text field: HTML → text, mojibake repair, unicode NFKC,
    zero-width removal, optional markdown/URL stripping, boilerplate-line
    removal, whitespace collapse. Returns "" for missing values and removal markers.
    """
    if is_missing(val):
        return ""
    text = str(val)
    if text.strip().lower() in REMOVED_MARKERS:
        return ""
    text = html_to_text(text)
    text = fix_mojibake(text, bare_a=repair_bare_a)
    text = unicodedata.normalize("NFKC", text)
    text = _ZERO_WIDTH.sub("", text).replace("\r\n", "\n").replace("\r", "\n")
    if markdown:
        text = strip_markdown(text)
    else:
        text = _URL.sub(" ", text)
    text = _BOILERPLATE.sub("", text)
    text = _TRAILING_BOILERPLATE.sub("", text)
    text = normalize_whitespace(text)
    if text.lower() in REMOVED_MARKERS:
        return ""
    return text


def split_gnews_publisher(headline: str) -> tuple[str, str | None]:
    """
    'Fed holds rates - Reuters' → ('Fed holds rates', 'Reuters').

    Also drops a repeated outlet tag before the suffix:
    'Inflation heats up | CNN Business - CNN' → ('Inflation heats up', 'CNN').
    """
    m = _GNEWS_PUBLISHER.search(headline)
    if not m:
        return headline, None
    title, publisher = headline[: m.start()].rstrip(), m.group(1).strip()
    first_word = publisher.split()[0].lower()
    head, sep, tail = title.rpartition(" | ")
    if sep and head and first_word in tail.lower():
        title = head.rstrip()
    return title, publisher


def normalize_for_hash(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace — basis for duplicate detection."""
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(normalize_for_hash(text).encode("utf-8")).hexdigest()[:32]


def drop_leading_headline(headline: str, body: str) -> str:
    """Remove a first body line that just repeats the headline (common in Fed releases)."""
    first, _, rest = body.partition("\n")
    if normalize_for_hash(first) and normalize_for_hash(first) == normalize_for_hash(headline):
        return rest.strip()
    return body


def body_repeats_headline(headline: str, body: str, *, max_extra_words: int = 6) -> bool:
    """
    True when the body adds nothing beyond the headline, e.g. Google News RSS
    descriptions ('<headline> <publisher>') or listing blurbs equal to the title.
    """
    h, b = normalize_for_hash(headline), normalize_for_hash(body)
    if not b:
        return True
    if not h:
        return False
    if b == h or b in h:
        return True
    if b.startswith(h):
        return len(b[len(h) :].split()) <= max_extra_words
    return False
