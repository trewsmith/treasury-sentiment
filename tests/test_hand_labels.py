import pandas as pd
import pytest

from src.labeling import hand_labels as hl


def _setup(tmp_path, monkeypatch, silver):
    monkeypatch.setattr(hl, "D", tmp_path)
    monkeypatch.setattr(hl, "LABELS", tmp_path / "labels.csv")
    pd.DataFrame({"doc_id": ["old"], "label": ["up"], "labeler": ["claude-silver"], "labeled_on": ["2026-01-01"]}).to_csv(
        hl.LABELS, index=False
    )
    pd.DataFrame({"doc_id": ["a", "b", "c"], "stratum": ["x"] * 3, "silver_label": silver}).to_csv(hl.key(9), index=False)


def test_merge_accepts_short_codes_and_blank_silver(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, silver=[None, None, None])
    pd.DataFrame({"row": [1, 2, 3], "doc_id": list("abc"), "hand_label": ["p", "N", "u"]}).to_csv(hl.sheet(9), index=False)
    hl.merge(9, "trew")
    out = pd.read_csv(hl.LABELS).set_index("doc_id")
    assert out.loc["a", "label"] == "up" and out.loc["b", "label"] == "down" and out.loc["c", "label"] == "neutral"
    assert out.loc["old", "label"] == "up" and (out.labeler == "trew").sum() == 3


def test_merge_rejects_invalid(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, silver=["up", "down", "neutral"])
    pd.DataFrame({"row": [1, 2, 3], "doc_id": list("abc"), "hand_label": ["up", "sideways", ""]}).to_csv(hl.sheet(9), index=False)
    with pytest.raises(SystemExit):
        hl.merge(9, "trew")


def test_regression_fit_recovers_signal():
    import numpy as np

    from src.modeling.daily_regression import fit

    rng = np.random.default_rng(0)
    x = rng.normal(size=600)
    df = pd.DataFrame({"y": 2.0 * x + rng.normal(size=600), "x": x, "event_day": 0.0})
    out = fit(df, "y", ["x"], "t", "t")
    assert abs(out[0]["coef_bp_per_sd"] - 2.0) < 0.3 and out[0]["p"] < 0.001


def test_intraday_fit_recovers_signal():
    import numpy as np

    from src.modeling.intraday_regression import fit

    rng = np.random.default_rng(1)
    x = rng.normal(size=800)
    df = pd.DataFrame({"y30": 1.5 * x + rng.normal(size=800), "news_ydir": x})
    out = fit(df, 30, ["news_ydir"], "t")
    assert abs(out[0]["coef_bp_per_sd"] - 1.5) < 0.3 and out[0]["horizon_min"] == 30


def test_event_study_helpers():
    import numpy as np

    from src.modeling.event_study import abs_move, perm_p

    idx = pd.date_range("2026-01-05 13:25", periods=20, freq="5min", tz="UTC")
    close = pd.Series(100.0, index=idx)
    close.iloc[2:] = 101.0  # +1% jump after the bar starting 13:30
    t = pd.Timestamp("2026-01-05 13:35", tz="UTC")  # price at T = close of bar starting 13:30
    assert abs_move(close, t, 5) == pytest.approx(np.log(1.01) * 1e4, rel=1e-6)
    assert np.isnan(abs_move(close, pd.Timestamp("2030-01-01", tz="UTC"), 5))
    assert perm_p(np.array([10.0] * 10), np.array([1.0] * 50), n=500) < 0.01
