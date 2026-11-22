import json

import pandas as pd
import pytest

from src.cleaning.documents import DOCUMENT_COLUMNS, expand_meta
from src.cleaning.language import detect_language
from src.cleaning.pipeline import add_time_alignment, build_documents, load_cleaning_config
from src.cleaning.text import (
    body_repeats_headline,
    clean_text,
    split_gnews_publisher,
    text_hash,
)
from src.ingestion.news.schema import records_to_frame as news_frame
from src.ingestion.reddit.schema import post_record, records_to_frame as reddit_frame


# --- text -------------------------------------------------------------------


def test_clean_text_html_and_boilerplate():
    raw = (
        "<p>May 10, 2018</p><p>The Fed plans a test &amp; more.</p>"
        "<p>For release at 10:00 a.m. EDT</p><p>For media inquiries, call 202-452-2955.</p>"
    )
    assert clean_text(raw) == "The Fed plans a test & more."


def test_clean_text_reddit_markdown():
    raw = "**Big** news: [Fed cuts](https://x.com/a_(b)) &amp;#x200B;\n\n> quoted\n\nsee https://t.co/x"
    assert clean_text(raw, markdown=True) == "Big news: Fed cuts\n\nquoted\n\nsee"


@pytest.mark.parametrize("marker", ["[removed]", "[deleted]", None, float("nan"), "  "])
def test_clean_text_markers_empty(marker):
    assert clean_text(marker, markdown=True) == ""


def test_clean_text_trailing_continue_reading():
    assert clean_text("Banks were bailed out. Continue reading...") == "Banks were bailed out."


def test_fix_mojibake_exact_sequences():
    assert clean_text("Appalachia\u00e2\u0080\u0099s coal") == "Appalachia’s coal"
    assert clean_text("2024 \u00e2\u0080\u0093 Mishustin") == "2024 – Mishustin"
    # Legitimate accents untouched
    assert clean_text("coup de grâce", markdown=True) == "coup de grâce"


def test_fix_bare_a_news_only():
    raw = "The Three Iâs: TreasuryâFederal at âGlobal Linkagesâ in 2023â2024 â¦"
    assert clean_text(raw, repair_bare_a=True) == (
        "The Three I's: Treasury-Federal at \"Global Linkages\" in 2023-2024 ..."  # NFKC: … → ...
    )
    assert "â" in clean_text(raw)  # not applied unless requested


def test_split_gnews_publisher():
    assert split_gnews_publisher("US yields drop - Reuters") == ("US yields drop", "Reuters")
    assert split_gnews_publisher("Inflation heats up | CNN Business - CNN") == (
        "Inflation heats up",
        "CNN",
    )
    # A pipe segment that is not the outlet stays
    assert split_gnews_publisher("FOMC cuts | 5 key highlights - Livemint")[0] == (
        "FOMC cuts | 5 key highlights"
    )
    assert split_gnews_publisher("No suffix here") == ("No suffix here", None)


def test_body_repeats_headline():
    assert body_repeats_headline("US yields drop", "US yields drop Reuters")
    assert body_repeats_headline("Fed holds", "")
    assert not body_repeats_headline("Fed holds", "The Fed held rates steady as inflation cooled.")


def test_text_hash_ignores_case_and_punctuation():
    assert text_hash("Fed Cuts Rates!") == text_hash("fed cuts   rates")
    assert text_hash("Fed cuts rates") != text_hash("Fed hikes rates")


# --- language -----------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "US Yield Curve - 10Y-2Y & 10Y-3M — Indicator by ValentinH",
        "Federal Reserve Board announces approval of application by Bank für Arbeit und Wirtschaft und Österreichische",
        "NVDA calls?",
        "Treasury yields rose after the jobs report beat expectations.",
    ],
)
def test_detect_language_english(text):
    assert detect_language(text) == "en"


@pytest.mark.parametrize(
    "text,lang",
    [
        ("La Ayuda al consumidor de la Reserva Federal ofrece una versión de su página en español", "es"),
        ("Was sagt ihr zu der Entwicklung? Ich bin mir nicht sicher, ob das für mich ist", "de"),
        ("美联储宣布维持利率不变，市场反应平淡", "non_latin"),
    ],
)
def test_detect_language_foreign(text, lang):
    assert detect_language(text) == lang


# --- end to end -----------------------------------------------------------------


def _market_csv(tmp_path):
    # Fri 2025-01-17, (Mon 2025-01-20 MLK holiday: DGS10 missing), Tue 2025-01-21
    path = tmp_path / "market_daily.csv"
    pd.DataFrame(
        {
            "date": ["2025-01-16", "2025-01-17", "2025-01-20", "2025-01-21"],
            "DGS10": [4.6, 4.61, None, 4.57],
        }
    ).to_csv(path, index=False)
    return path


def _news():
    rows = [
        # FOMC-style release, 14:00 ET Thu → same-day yield
        dict(article_id="n1", source="federal_reserve", headline="Federal Reserve issues FOMC statement",
             body="<p>January 16, 2025</p><p>Federal Reserve issues FOMC statement</p>"
                  "<p>Inflation remains somewhat elevated.</p><p>For media inquiries, call 202-452-2955.</p>",
             published_at_utc="2025-01-16T19:00:00Z", url="https://federalreserve.gov/a", section="Monetary Policy"),
        # Google News: body repeats headline → dropped; after 15:30 Fri → next obs = Tue (holiday Mon)
        dict(article_id="n2", source="google_news", headline="US yields climb as data surprises - Reuters",
             body='<a href="https://news.google.com/x">US yields climb as data surprises</a>&nbsp;<font>Reuters</font>',
             published_at_utc="2025-01-17T21:00:00Z", url="https://news.google.com/x"),
        # Same story syndicated 2h later on another URL → hash dup
        dict(article_id="n3", source="cnbc", headline="US yields climb as data surprises",
             body=None, published_at_utc="2025-01-17T23:00:00Z", url="https://cnbc.com/x"),
        # Date-only Fed stamp (00:00 ET)
        dict(article_id="n4", source="federal_reserve", headline="Speech by Governor Waller on the economic outlook",
             body=None, published_at_utc="2025-01-16T05:00:00Z", url="https://federalreserve.gov/b", section="speech"),
        # No timestamp → dropped
        dict(article_id="n5", source="yahoo_finance", headline="I Bonds could approach 5% this fall",
             body=None, published_at_utc=None, url="https://yahoo.com/x"),
        # Too short (< 3 words)
        dict(article_id="n6", source="cnbc", headline="Markets Live", body=None,
             published_at_utc="2025-01-16T15:00:00Z", url="https://cnbc.com/y"),
    ]
    return news_frame(rows)


def _posts():
    raws = [
        dict(id="r1", subreddit="bonds", title="Why did the 10 year yield jump today?",
             selftext="Seems like **CPI** was hot. Thoughts? https://example.com", created_utc=1737046800,
             score=5, retrieved_on=1737046900),  # 2025-01-16 12:00 ET
        dict(id="r2", subreddit="wallstreetbets", title="Look at my loss porn from today lol",
             selftext="[removed]", removed_by_category="moderator", created_utc=1737046800),
        dict(id="r3", subreddit="wallstreetbets", title="Daily Discussion Thread for January 16, 2025",
             selftext="", created_utc=1737046800, author="OPINION_IS_UNPOPULAR"),
        dict(id="r4", subreddit="investing", title="Daily General Discussion and Advice Thread",
             selftext="", created_utc=1737046800, author="AutoModerator", stickied=True),
        dict(id="r5", subreddit="stocks", title="Bonds?", selftext="", created_utc=1737046800),
        # Crosspost of r1 within an hour → hash dup of r1
        dict(id="r6", subreddit="investing", title="Why did the 10 year yield jump today?",
             selftext="Seems like CPI was hot. Thoughts?", created_utc=1737050400),
        # Saturday post by deleted account with surviving text → kept, weekend session
        dict(id="r7", subreddit="economics", title="Long bond auction next week looks shaky to me",
             selftext=None, author="[deleted]", created_utc=1737216000),  # Sat 2025-01-18 11:00 ET
    ]
    return reddit_frame([post_record(r, ingest_method="arctic_shift") for r in raws])


@pytest.fixture
def result(tmp_path):
    cfg = load_cleaning_config()
    return build_documents(cfg, _news(), _posts(), market_path=_market_csv(tmp_path))


def test_output_schema(result):
    docs = result.docs
    assert list(docs.columns) == DOCUMENT_COLUMNS
    assert docs["doc_id"].is_unique
    assert str(docs["timestamp_utc"].dtype) == "datetime64[us, UTC]"


def test_expected_documents_kept(result):
    assert set(result.docs["doc_id"]) == {
        "news:n1", "news:n2", "news:n4", "reddit:r1", "reddit:r7",
    }


def test_funnel_accounts_for_every_row(result):
    dropped = {st: sum(c[st] for _, c in result.funnel.steps) for st in ("news", "reddit")}
    kept = result.docs["source_type"].value_counts()
    assert dropped["news"] + kept["news"] == len(_news())
    assert dropped["reddit"] + kept["reddit"] == len(_posts())


def test_fed_body_cleaned(result):
    row = result.docs.set_index("doc_id").loc["news:n1"]
    assert row["body"] == "Inflation remains somewhat elevated."
    assert row["text"] == "Federal Reserve issues FOMC statement\n\nInflation remains somewhat elevated."


def test_google_news_publisher_and_redundant_body(result):
    row = result.docs.set_index("doc_id").loc["news:n2"]
    assert row["headline"] == "US yields climb as data surprises"
    assert pd.isna(row["body"])
    assert json.loads(row["meta"])["publisher"] == "Reuters"


def test_reddit_text_cleaned(result):
    row = result.docs.set_index("doc_id").loc["reddit:r1"]
    assert row["body"] == "Seems like CPI was hot. Thoughts?"
    assert row["source_name"] == "r/bonds"


def test_time_alignment(result):
    d = result.docs.set_index("doc_id")
    # 14:00 ET Thursday → regular session, same-day yield
    assert d.loc["news:n1", "market_session"] == "regular"
    assert d.loc["news:n1", "yield_date"] == pd.Timestamp("2025-01-16")
    # 16:00 ET Friday (after 15:30 cutoff) → skip weekend + MLK holiday → Tue
    assert d.loc["news:n2", "et_date"] == pd.Timestamp("2025-01-17")
    assert d.loc["news:n2", "market_session"] == "post"
    assert d.loc["news:n2", "yield_date"] == pd.Timestamp("2025-01-21")
    # Date-only stamp is flagged and labelled
    assert d.loc["news:n4", "timestamp_is_date_only"]
    assert d.loc["news:n4", "market_session"] == "date_only"
    assert not d.loc["reddit:r1", "timestamp_is_date_only"]
    # Saturday post
    assert d.loc["reddit:r7", "market_session"] == "weekend"
    assert d.loc["reddit:r7", "yield_date"] == pd.Timestamp("2025-01-21")


def test_yield_date_null_past_market_data(tmp_path):
    cfg = load_cleaning_config()
    docs = pd.DataFrame(
        {"source_type": ["news"], "timestamp_utc": pd.to_datetime(["2030-01-02T15:00:00Z"])}
    )
    out = add_time_alignment(docs, cfg, _market_csv(tmp_path))
    assert pd.isna(out.loc[0, "yield_date"])


def test_expand_meta(result):
    flat = expand_meta(result.docs)
    r = flat.set_index("doc_id")
    assert r.loc["reddit:r1", "meta_score"] == 5
    assert r.loc["news:n1", "meta_section"] == "Monetary Policy"
    assert pd.isna(r.loc["news:n1", "meta_score"])
