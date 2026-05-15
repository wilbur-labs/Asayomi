"""Smoke tests for ai_processor — JSON parsing + EN translation paths.

Uses MockAzureClient (see conftest) so no real Azure OpenAI call is made.
Locks in current behavior ahead of P1-5 (split the nested try/except).
"""
import json
from datetime import datetime, timezone

from app.models.article import Article
from app.services.ai_processor import process_article


def _make_article(language="ja", title="原タイトル"):
    return Article(
        title=title,
        original_title=title,
        url="https://example.com/x",
        source="NHK News Web",
        language=language,
        category="総合",
        original_content="本文の冒頭",
        full_content="本文全体",
        processed=False,
        importance_score=0.0,
        published_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
        collected_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
    )


def test_japanese_article_sets_summary_category_score_tags(mock_openai_client):
    payload = json.dumps({
        "summary": "短い要約",
        "category": "テクノロジー",
        "score": 8,
        "tags": "AI,半導体,日本",
    })
    client = mock_openai_client(payload)
    article = _make_article(language="ja")

    ok = process_article(client, article)
    assert ok is True
    assert article.summary == "短い要約"
    assert article.category == "テクノロジー"
    assert article.importance_score == 8.0
    assert article.tags == "AI,半導体,日本"
    assert article.processed is True
    assert article.title == "原タイトル"


def test_english_article_overwrites_title_with_translation(mock_openai_client):
    payload = json.dumps({
        "translated_title": "翻訳されたタイトル",
        "summary": "要約",
        "category": "国際",
        "score": 7,
        "tags": "海外",
    })
    client = mock_openai_client(payload)
    article = _make_article(language="en", title="English Title")

    ok = process_article(client, article)
    assert ok is True
    assert article.title == "翻訳されたタイトル"
    assert article.original_title == "English Title"


def test_malformed_json_returns_false_and_keeps_unprocessed(mock_openai_client):
    client = mock_openai_client("this is not json")
    article = _make_article()
    ok = process_article(client, article)
    assert ok is False
    assert article.processed is False
    assert article.summary is None or article.summary == ""


def test_missing_fields_fall_back_to_defaults(mock_openai_client):
    payload = json.dumps({"summary": "only summary"})
    client = mock_openai_client(payload)
    article = _make_article()

    ok = process_article(client, article)
    assert ok is True
    assert article.summary == "only summary"
    # category falls back to existing value
    assert article.category == "総合"
    # score falls back to 5 per ai_processor.py
    assert article.importance_score == 5.0
    assert article.tags == ""
