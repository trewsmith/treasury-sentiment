import json

import numpy as np
import pandas as pd
import pytest

from src.features.pipeline import add_surprise, aggregate, build_intraday, document_weights, prepare
from src.nlp import yield_classifier as yc
from src.nlp.sentiment import derive_scores, score_vader
from src.nlp.taxonomy import load_taxonomy, relevance_mask, tag_topics, yield_rule_features
from src.nlp.transformer_scoring import _label_map


@pytest.fixture(scope="module")
def tax():
    return load_taxonomy()


# --- taxonomy -------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,label",
    [
        ("Treasuries rally on recession fears", "down"),
        ("Bond yields climb after hot CPI report", "up"),
        ("Fed signals fewer rate cuts as inflation stays sticky", "up"),
        ("Fed cuts rates by 50 basis points", "down"),
        ("Stocks plunge as banking crisis spreads; investors flee to safe havens", "down"),
        ("Strong jobs report: payrolls beat estimates", "up"),
        ("10-year yield falls to three-month low", "down"),
        ("Fed pauses rate hikes", "down"),
        ("Bond prices fall as supply worries mount", "up"),
        ("Mortgage Rates Today: 30-Year Rates Climb to 7.02%", "up"),
        ("Mortgage rates fall to lowest level in a year", "down"),
        ("With inflation increasing once more, TIPS look attractive", "up"),
        ("GDPNow Estimate +4.6% now", "up"),
        ("Apple unveils new iPhone", "none"),
    ],
)
def test_yield_rules(tax, text, label):
    out = yield_rule_features(pd.Series([text]), tax["yield_direction"])
    assert out.loc[0, "yield_rule_label"] == label


def test_bond_yields_phrase_not_double_counted(tax):
    """'bond yields climb' must not also count as bonds (prices) climbing."""
    out = yield_rule_features(pd.Series(["Bond yields climb"]), tax["yield_direction"])
    assert out.loc[0, "yield_rule_down_hits"] == 0


def test_offsetting_cues_are_ambiguous(tax):
    out = yield_rule_features(
        pd.Series(["Yields rise early, then yields fall after the auction"]), tax["yield_direction"]
    )
    assert out.loc[0, "yield_rule_label"] == "ambiguous"


def test_topics_multilabel(tax):
    out = tag_topics(pd.Series(["Powell says CPI inflation is sticky", "Nice dog"]), tax["topics"])
    assert out.loc[0, "topics"] == "inflation|fed"
    assert out.loc[0, "n_topics"] == 2
    assert out.loc[1, "topics"] == "" and out.loc[1, "n_topics"] == 0


def test_relevance_mask(tax):
    texts = pd.Series(["Nice dog", "Nice dog", "Yields jump"])
    st = pd.Series(["news", "reddit", "reddit"])
    m = relevance_mask(st, tag_topics(texts, tax["topics"]), yield_rule_features(texts, tax["yield_direction"]))
    assert m.tolist() == [True, False, True]


# --- sentiment --------------------------------------------------------------------


def test_derive_scores():
    probs = pd.DataFrame(
        {"p_positive": [0.7, 0.5, np.nan], "p_neutral": [0.2, 0.0, np.nan], "p_negative": [0.1, 0.5, np.nan]}
    )
    out = derive_scores(probs, "m", 3)
    assert out.loc[0, "m_sentiment_score"] == pytest.approx(0.6)
    assert out.loc[0, "m_confidence"] == pytest.approx(0.7)
    assert 0 < out.loc[0, "m_entropy"] < 1
    # Binary model at 50/50 is maximally uncertain over its 2 classes
    assert derive_scores(probs.iloc[[1]], "b", 2).iloc[0]["b_entropy"] == pytest.approx(1.0)
    assert out.loc[2, ["m_sentiment_score", "m_confidence", "m_entropy"]].isna().all()


def test_vader_direction():
    out = score_vader(pd.Series(["Great, wonderful results!", "Terrible, awful crash."]))
    assert out.loc[0, "vader_sentiment_score"] > 0 > out.loc[1, "vader_sentiment_score"]
    probs = out[["vader_p_positive", "vader_p_neutral", "vader_p_negative"]].sum(axis=1)
    assert np.allclose(probs, 1.0, atol=0.01)


def test_label_map():
    assert _label_map({0: "positive", 1: "negative", 2: "neutral"}) == {
        0: "p_positive", 1: "p_negative", 2: "p_neutral",
    }
    assert _label_map({0: "NEGATIVE", 1: "POSITIVE"}) == {0: "p_negative", 1: "p_positive"}
    with pytest.raises(ValueError):
        _label_map({0: "LABEL_0"})


# --- yield classifier ----------------------------------------------------------------


def test_classifier_fit_predict(tax):
    texts = (
        ["yields jump on hot inflation"] * 6
        + ["treasuries rally as recession fears grow"] * 6
        + ["my dog likes the park today"] * 6
    )
    df = pd.DataFrame({"text": texts, "label": ["up"] * 6 + ["down"] * 6 + ["neutral"] * 6})
    df = pd.concat([df, yield_rule_features(df["text"], tax["yield_direction"])], axis=1)
    model, proba = yc.fit_predict(df, df)
    assert list(proba.columns) == ["yield_p_up", "yield_p_down", "yield_p_neutral"]
    assert np.allclose(proba.sum(axis=1), 1.0)
    assert proba.loc[0, "yield_p_up"] > 0.5 and proba.loc[6, "yield_p_down"] > 0.5
    ev = yc.evaluate(df, folds=3)
    assert ev.model_macro_f1 > 0.9


def test_rule_baseline():
    s = pd.Series(["up", "down", "ambiguous", "none"])
    assert yc.rule_baseline(s).tolist() == ["up", "down", "neutral", "neutral"]


# --- features ----------------------------------------------------------------------


def _scored():
    ts = pd.to_datetime(
        ["2025-01-02T15:00:00Z", "2025-01-02T15:03:00Z", "2025-01-02T15:20:00Z", "2025-01-03T15:00:00Z"]
    )
    return pd.DataFrame(
        {
            "source_type": ["news", "reddit", "reddit", "news"],
            "source_name": ["google_news", "r/bonds", "r/bonds", "cnbc"],
            "meta": [
                json.dumps({"publisher": "Reuters"}),
                json.dumps({"score": 0}),
                json.dumps({"score": 99}),
                json.dumps({}),
            ],
            "timestamp_utc": ts,
            "yield_date": pd.to_datetime(["2025-01-02", "2025-01-02", "2025-01-02", "2025-01-03"]),
            "timestamp_is_date_only": [False] * 4,
            "is_relevant": [True, True, False, True],
            "finbert_sentiment_score": [0.5, -0.8, np.nan, 0.1],
            "vader_sentiment_score": [0.1, -0.2, 0.3, 0.0],
            "yield_direction_signal": [0.6, -0.4, 0.9, 0.2],
            "topic_inflation": [True, False, False, False],
            "topic_fed": [False, True, False, True],
        }
    )


CFG = {
    "sentiment_model": "finbert",
    "negative_spike_threshold": -0.5,
    "topic_features": ["inflation", "fed"],
    "news_weights": {"default_weight": 0.5, "sources": {"cnbc": 0.8},
                     "google_news_publishers": {"Reuters": 1.0}},
    "intraday": {"start_date": "2025-01-01", "frequencies": ["5min"], "shock_lookback": "30min"},
}


def test_document_weights():
    w = document_weights(_scored(), CFG)
    assert w.tolist() == pytest.approx([1.0, 1.0, 1.0 + np.log1p(99), 0.8])


def test_daily_aggregate():
    prep = prepare(_scored(), CFG)
    daily = aggregate(prep, "yield_date", CFG)
    d0 = daily.loc[pd.Timestamp("2025-01-02")]
    assert d0["n_news"] == 1 and d0["n_reddit"] == 2 and d0["n_reddit_relevant"] == 1
    assert d0["reddit_sent_mean"] == pytest.approx(-0.8)  # NaN score ignored
    assert d0["reddit_neg_spike"] == 1
    # yield direction only from the relevant reddit doc
    assert d0["reddit_ydir_mean"] == pytest.approx(-0.4)
    assert d0["n_topic_inflation"] == 1
    assert d0["news_inflation_sent_mean"] == pytest.approx(0.5)


def test_surprise_uses_only_prior_periods():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 100.0]})
    out = add_surprise(df, ["x"], window=3, min_periods=3)
    prior = np.array([2.0, 3.0, 4.0])
    assert out.loc[4, "x_z3"] == pytest.approx((100 - prior.mean()) / prior.std(ddof=1))
    assert out["x_z3"].iloc[:3].isna().all()


def test_intraday_buckets():
    out = build_intraday(prepare(_scored(), CFG), CFG)
    first = out.set_index("bucket_start_utc").loc[pd.Timestamp("2025-01-02T15:00:00Z")]
    assert first["n_news"] == 1 and first["n_reddit"] == 1
    # complete 5-minute grid from first to last bucket
    assert len(out) == (pd.Timestamp("2025-01-03T15:00Z") - pd.Timestamp("2025-01-02T15:00Z")) / pd.Timedelta("5min") + 1
    assert first["ydir_pressure"] == pytest.approx(0.6 * 1.0 + -0.4 * 1.0)


def test_build_model_options_and_label_validation(tmp_path):
    df = pd.DataFrame(
        {
            "text": ["yields jump"] * 4 + ["yields fall"] * 4 + ["nothing here"] * 4,
            "label": ["up"] * 4 + ["down"] * 4 + ["neutral"] * 4,
            "yield_rule_up_hits": [1] * 4 + [0] * 8,
            "yield_rule_down_hits": [0] * 4 + [1] * 4 + [0] * 4,
            "finbert_sentiment_score": [0.5] * 4 + [-0.5] * 4 + [0.0] * 4,
        }
    )
    cols = ["text", *yc.RULE_FEATURES, "finbert_sentiment_score"]
    m = yc.build_model(C=1.0, max_chars=5, extra_features=["finbert_sentiment_score"]).fit(df[cols], df["label"])
    assert set(m.predict(df[cols])) <= set(yc.LABELS)
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"doc_id": ["a"], "label": ["sideways"]}).to_csv(bad, index=False)
    with pytest.raises(ValueError):
        yc.load_labels(bad)


def test_model_is_picklable(tmp_path):
    import joblib

    joblib.dump(yc.build_model(max_chars=100), tmp_path / "m.joblib")
