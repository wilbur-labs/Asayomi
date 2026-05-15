"""chat._format_context — locks down the operator-precedence fix.

Before this fix, when `original_content` was None, the entire snippet
expression evaluated to "" — silently dropping summary even if present.
"""
from app.models.article import Article
from app.services.chat import _format_context


def _make(summary=None, original_content=None, title="記事", url="https://x"):
    return Article(
        title=title,
        original_title=title,
        url=url,
        source="NHK News Web",
        language="ja",
        category="総合",
        summary=summary,
        original_content=original_content,
        importance_score=5.0,
    )


def test_uses_summary_when_present_even_if_original_content_is_none():
    out = _format_context([_make(summary="これが要約", original_content=None)])
    assert "これが要約" in out


def test_falls_back_to_original_content_when_no_summary():
    a = _make(summary=None, original_content="これは生本文" * 5)
    out = _format_context([a])
    # Truncated to 120 chars per chat.py
    assert "これは生本文" in out


def test_empty_when_neither_set():
    a = _make(summary=None, original_content=None)
    out = _format_context([a])
    # Summary line is present but empty after the prefix
    assert "要約: \n" in out
