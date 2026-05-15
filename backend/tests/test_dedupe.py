"""Smoke tests for dedupe.detect_duplicates — title similarity, same-source skip."""
from datetime import datetime, timezone, timedelta

from app.models.article import Article
from app.services.dedupe import detect_duplicates


def _add(db, title, source, hours_ago=1, url=None):
    db.add(
        Article(
            title=title,
            original_title=title,
            url=url or f"https://example.com/{source}/{title[:8]}",
            source=source,
            language="ja",
            category="総合",
            collected_at=datetime.now(timezone.utc) - timedelta(hours=hours_ago),
            is_duplicate=False,
        )
    )
    db.commit()


def test_marks_near_duplicate_across_sources(db_session):
    _add(db_session, "首相が新政策を発表した", "NHK News Web", hours_ago=2)
    _add(db_session, "首相が新政策を発表した模様", "Yahoo!ニュース", hours_ago=1)
    marked = detect_duplicates()
    assert marked == 1
    later = (
        db_session.query(Article)
        .filter(Article.source == "Yahoo!ニュース")
        .first()
    )
    assert later.is_duplicate is True
    assert later.duplicate_of_id is not None


def test_same_source_does_not_dedupe(db_session):
    # Two near-identical entries from same source — should NOT be marked
    # (per dedupe.py:48 "同じソース内での再投稿は無視").
    _add(db_session, "首相が新政策を発表", "NHK News Web", hours_ago=2, url="https://x/1")
    _add(db_session, "首相が新政策を発表した", "NHK News Web", hours_ago=1, url="https://x/2")
    marked = detect_duplicates()
    assert marked == 0


def test_dissimilar_titles_not_marked(db_session):
    _add(db_session, "天気予報：明日は晴れ", "NHK News Web", hours_ago=2)
    _add(db_session, "プロ野球：阪神が勝利", "Yahoo!ニュース", hours_ago=1)
    marked = detect_duplicates()
    assert marked == 0


def test_outside_window_not_compared(db_session):
    _add(db_session, "首相が新政策を発表した", "NHK News Web", hours_ago=100)
    _add(db_session, "首相が新政策を発表した", "Yahoo!ニュース", hours_ago=1)
    marked = detect_duplicates(window_hours=48)
    # The 100h-old article is outside the window, so the 1h-old one has
    # nothing to compare against → not marked.
    assert marked == 0
