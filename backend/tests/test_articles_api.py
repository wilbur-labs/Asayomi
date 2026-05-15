"""Smoke tests for /api/v1/articles list & detail endpoints.

Locks in current behavior ahead of:
- P1-3 (tags Column(String) → array/tag-table refactor)
- P1-1 (frontend ArticlesPage split — must not change the contract)
"""
from datetime import datetime, timezone

from app.models.article import Article


def _seed(db, **overrides):
    defaults = dict(
        title="サンプル記事",
        original_title="サンプル記事",
        url=f"https://example.com/{overrides.get('id', 1)}",
        source="NHK News Web",
        language="ja",
        category="総合",
        summary="要約",
        importance_score=5.0,
        tags="政治,経済",
        published_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        collected_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        processed=True,
        is_duplicate=False,
        is_favorite=False,
        is_read=False,
    )
    defaults.update(overrides)
    defaults.pop("id", None)
    a = Article(**defaults)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_list_empty(client):
    r = client.get("/api/v1/articles")
    assert r.status_code == 200
    body = r.json()
    assert body == {"total": 0, "articles": []}


def test_list_returns_seeded_article(client, db_session):
    _seed(db_session, url="https://example.com/1")
    r = client.get("/api/v1/articles")
    body = r.json()
    assert body["total"] == 1
    assert len(body["articles"]) == 1
    a = body["articles"][0]
    # API contract: tags is a list, not a comma-separated string
    assert a["tags"] == ["政治", "経済"]
    assert a["category"] == "総合"
    assert a["is_favorite"] is False


def test_list_excludes_duplicates_by_default(client, db_session):
    _seed(db_session, url="https://example.com/1")
    _seed(db_session, url="https://example.com/2", is_duplicate=True)
    r = client.get("/api/v1/articles")
    assert r.json()["total"] == 1


def test_list_include_duplicates_flag(client, db_session):
    _seed(db_session, url="https://example.com/1")
    _seed(db_session, url="https://example.com/2", is_duplicate=True)
    r = client.get("/api/v1/articles?include_duplicates=true")
    assert r.json()["total"] == 2


def test_list_category_filter(client, db_session):
    _seed(db_session, url="https://example.com/1", category="総合")
    _seed(db_session, url="https://example.com/2", category="テクノロジー")
    r = client.get("/api/v1/articles?category=テクノロジー")
    body = r.json()
    assert body["total"] == 1
    assert body["articles"][0]["category"] == "テクノロジー"


def test_list_favorite_only(client, db_session):
    _seed(db_session, url="https://example.com/1", is_favorite=False)
    _seed(db_session, url="https://example.com/2", is_favorite=True)
    r = client.get("/api/v1/articles?favorite_only=true")
    assert r.json()["total"] == 1


def test_list_pagination_limit_offset(client, db_session):
    for i in range(5):
        _seed(db_session, url=f"https://example.com/{i}", importance_score=float(i))
    r = client.get("/api/v1/articles?limit=2&offset=1")
    body = r.json()
    assert body["total"] == 5  # total ignores limit/offset
    assert len(body["articles"]) == 2


def test_get_single_article_includes_full_content(client, db_session):
    a = _seed(db_session, url="https://example.com/1", full_content="長い本文…")
    r = client.get(f"/api/v1/articles/{a.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["full_content"] == "長い本文…"


def test_get_404_for_missing_article(client):
    r = client.get("/api/v1/articles/99999")
    assert r.status_code == 404
