"""Smoke tests for search.search_articles — LIKE-based, hybrid CJK/ASCII."""
from datetime import datetime, timezone

from app.models.article import Article
from app.services.search import search_articles


def _add(db, title, summary="", tags="", language="ja", is_duplicate=False, url=None):
    db.add(
        Article(
            title=title,
            original_title=title,
            url=url or f"https://example.com/{title[:8]}",
            source="NHK News Web",
            language=language,
            category="総合",
            summary=summary,
            tags=tags,
            published_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
            collected_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
            is_duplicate=is_duplicate,
            importance_score=5.0,
        )
    )
    db.commit()


def test_returns_empty_for_empty_query(db_session):
    assert search_articles("") == []
    assert search_articles("   ") == []


def test_single_term_matches_title(db_session):
    _add(db_session, "AI が金融業界を変える")
    _add(db_session, "天気予報")
    out = search_articles("AI")
    assert len(out) == 1
    assert "AI" in out[0]["title"]


def test_multi_term_is_and(db_session):
    _add(db_session, "AI と金融", url="https://example.com/a")
    _add(db_session, "AI と医療", url="https://example.com/b")
    _add(db_session, "金融と政治", url="https://example.com/c")
    out = search_articles("AI 金融")
    assert len(out) == 1  # only the article containing BOTH terms
    assert out[0]["title"] == "AI と金融"


def test_matches_against_tags_field(db_session):
    _add(db_session, "無関係タイトル", tags="量子計算,物理学")
    out = search_articles("量子計算")
    assert len(out) == 1


def test_excludes_duplicates(db_session):
    _add(db_session, "重要ニュース", url="https://example.com/1", is_duplicate=False)
    _add(db_session, "重要ニュース", url="https://example.com/2", is_duplicate=True)
    out = search_articles("重要ニュース")
    assert len(out) == 1
