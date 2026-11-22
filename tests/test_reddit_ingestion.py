from datetime import datetime, timezone

import pandas as pd
import pytest

from src.ingestion.reddit import arctic_shift
from src.ingestion.reddit.arctic_shift import fetch_window, month_windows
from src.ingestion.reddit.pipeline import dedupe_posts
from src.ingestion.reddit.schema import REDDIT_POST_COLUMNS, post_record, records_to_frame

UTC = timezone.utc


def _raw(pid, ts, **kw):
    return {"id": pid, "subreddit": "Bonds", "title": f"t{pid}", "created_utc": ts, **kw}


def test_post_record_normalizes_fields():
    rec = post_record(
        _raw(
            "abc",
            1738362415,
            selftext="",
            permalink="/r/bonds/comments/abc/x/",
            retrieved_on=1738362500,
            score=6,
        ),
        ingest_method="arctic_shift",
    )
    assert rec["post_id"] == "abc"
    assert rec["subreddit"] == "bonds"
    assert rec["selftext"] is None
    assert rec["permalink"] == "https://www.reddit.com/r/bonds/comments/abc/x/"
    assert rec["created_utc"] == pd.Timestamp("2025-01-31 22:26:55", tz="UTC")
    assert rec["score_observed_at_utc"] == pd.Timestamp(1738362500, unit="s", tz="UTC")


def test_post_record_prefers_second_retrieval_time():
    rec = post_record(
        _raw("abc", 1000, retrieved_on=1010, _meta={"retrieved_2nd_on": 1000 + 36 * 3600}),
        ingest_method="arctic_shift",
    )
    assert rec["score_observed_at_utc"] == pd.Timestamp(1000 + 36 * 3600, unit="s", tz="UTC")


def test_post_record_builds_permalink_when_missing():
    rec = post_record({"id": "t3_xyz", "subreddit": "stocks", "title": "x"}, ingest_method="praw")
    assert rec["post_id"] == "xyz"
    assert rec["permalink"] == "https://www.reddit.com/r/stocks/comments/xyz/"


def test_records_to_frame_schema_and_dtypes():
    df = records_to_frame([post_record(_raw("a", 1, score=3), ingest_method="arctic_shift")])
    assert list(df.columns) == REDDIT_POST_COLUMNS
    assert str(df["created_utc"].dtype).endswith("UTC]")
    assert str(df["score"].dtype) == "Int64"


def test_month_windows_clips_bounds():
    w = month_windows(datetime(2025, 1, 15, tzinfo=UTC), datetime(2025, 3, 2, 5, tzinfo=UTC))
    assert w == [
        (datetime(2025, 1, 15, tzinfo=UTC), datetime(2025, 2, 1, tzinfo=UTC)),
        (datetime(2025, 2, 1, tzinfo=UTC), datetime(2025, 3, 1, tzinfo=UTC)),
        (datetime(2025, 3, 1, tzinfo=UTC), datetime(2025, 3, 2, 5, tzinfo=UTC)),
    ]


def test_month_windows_crosses_year():
    w = month_windows(datetime(2025, 12, 1, tzinfo=UTC), datetime(2026, 2, 1, tzinfo=UTC))
    assert [a.month for a, _ in w] == [12, 1]


def test_fetch_window_paginates_with_ties(monkeypatch):
    """Posts sharing the page-boundary second must not be lost (API `after` is exclusive)."""
    posts = [_raw(f"p{i}", 1000 + i // 3) for i in range(10)]  # 3 posts per second

    def fake_get_page(session, base_url, params):
        after, before, limit = params["after"], params["before"], params["limit"]
        hits = [p for p in posts if after < p["created_utc"] < before]
        return hits[:limit]

    monkeypatch.setattr(arctic_shift, "_get_page", fake_get_page)
    df = fetch_window(
        "bonds",
        datetime.fromtimestamp(1000, UTC),
        datetime.fromtimestamp(2000, UTC),
        session=object(),
        page_size=4,
        sleep_seconds=0,
    )
    assert sorted(df["post_id"]) == sorted(p["id"] for p in posts)
    assert df["post_id"].is_unique


def test_fetch_window_excludes_end_bound(monkeypatch):
    posts = [_raw("in", 1500), _raw("edge", 2000)]
    monkeypatch.setattr(
        arctic_shift,
        "_get_page",
        lambda s, u, p: [x for x in posts if p["after"] < x["created_utc"] <= p["before"]][: p["limit"]],
    )
    df = fetch_window(
        "bonds",
        datetime.fromtimestamp(1000, UTC),
        datetime.fromtimestamp(2000, UTC),
        session=object(),
        sleep_seconds=0,
    )
    assert df["post_id"].tolist() == ["in"]


def test_get_page_retries_api_timeout(monkeypatch):
    calls = []

    class Resp:
        def __init__(self, payload):
            self.status_code, self.headers, self._p = 200, {}, payload

        def raise_for_status(self):
            pass

        def json(self):
            return self._p

    class Sess:
        def get(self, *a, **k):
            calls.append(1)
            if len(calls) == 1:
                return Resp({"data": None, "error": "Timeout. Maybe slow down a bit"})
            return Resp({"data": [{"id": "x"}]})

    monkeypatch.setattr(arctic_shift.time, "sleep", lambda s: None)
    assert arctic_shift._get_page(Sess(), "u", {}) == [{"id": "x"}]
    assert len(calls) == 2


def test_get_page_gives_up(monkeypatch):
    class Resp:
        status_code, headers = 503, {}

    class Sess:
        def get(self, *a, **k):
            return Resp()

    monkeypatch.setattr(arctic_shift.time, "sleep", lambda s: None)
    with pytest.raises(arctic_shift.ArcticShiftError):
        arctic_shift._get_page(Sess(), "u", {})


def test_dedupe_posts_prefers_archive_row():
    archive = post_record(_raw("a", 1, score=2), ingest_method="arctic_shift")
    fresh = post_record(_raw("a", 1, score=900), ingest_method="praw")
    other = post_record(_raw("b", 2), ingest_method="praw")
    out = dedupe_posts(records_to_frame([fresh, archive, other]))
    assert out["post_id"].tolist() == ["a", "b"]
    assert out.loc[0, "ingest_method"] == "arctic_shift"
    assert out.loc[0, "score"] == 2
