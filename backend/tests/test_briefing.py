"""Smoke tests for briefing._generate_for_window — category grouping + filters.

Locks in current behavior ahead of P1-9 (DailyBriefing.date column refactor).
"""
from datetime import datetime, timezone

from app.models.article import Article, DailyBriefing
from app.services.briefing import generate_briefing


def _add(db, title, category, *, processed=True, is_duplicate=False, score=5.0, when=None):
    db.add(
        Article(
            title=title,
            original_title=title,
            url=f"https://example.com/{title[:10]}",
            source="NHK News Web",
            language="ja",
            category=category,
            summary=f"{title} の要約",
            importance_score=score,
            tags="",
            published_at=when or datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
            collected_at=when or datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
            processed=processed,
            is_duplicate=is_duplicate,
        )
    )
    db.commit()


def test_generates_one_briefing_per_category_with_articles(db_session):
    _add(db_session, "総合ニュース", "総合")
    _add(db_session, "テックニュース", "テクノロジー")
    count = generate_briefing("2026-05-15")
    assert count == 2

    briefings = db_session.query(DailyBriefing).filter(DailyBriefing.date == "2026-05-15").all()
    cats = sorted(b.category for b in briefings)
    assert cats == ["テクノロジー", "総合"]


def test_skips_categories_without_processed_articles(db_session):
    # Only one article, and it's still unprocessed.
    _add(db_session, "未処理", "総合", processed=False)
    count = generate_briefing("2026-05-15")
    assert count == 0


def test_skips_duplicate_articles(db_session):
    _add(db_session, "重複記事", "総合", is_duplicate=True)
    count = generate_briefing("2026-05-15")
    assert count == 0


def test_regenerate_replaces_existing(db_session):
    _add(db_session, "古い", "総合")
    generate_briefing("2026-05-15")
    # Same date, regenerate — the old row should be replaced, not duplicated.
    generate_briefing("2026-05-15")
    rows = db_session.query(DailyBriefing).filter(
        DailyBriefing.date == "2026-05-15",
        DailyBriefing.category == "総合",
    ).count()
    assert rows == 1
