"""Smoke tests for notify.render_briefing_html — HTML escape + markdown-lite."""
from datetime import datetime, timezone

from app.models.article import DailyBriefing
from app.services.notify import _render_markdown_lite, render_briefing_html


def test_escapes_script_tags():
    out = _render_markdown_lite("<script>alert(1)</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_bold_markdown_to_b_tag_multiple_pairs():
    out = _render_markdown_lite("**A** と **B** の比較")
    assert out.count("<b>") == 2
    assert out.count("</b>") == 2


def test_bare_urls_are_linkified():
    out = _render_markdown_lite("see https://example.com/x")
    assert '<a href="https://example.com/x">https://example.com/x</a>' in out


def test_url_ampersand_gets_escaped():
    out = _render_markdown_lite("https://example.com/?a=1&b=2")
    # & must be escaped to &amp; (the linkifier runs on the escaped string)
    assert "&amp;" in out
    assert "&b=2" not in out


def test_newlines_become_br():
    out = _render_markdown_lite("line1\nline2")
    assert "<br>" in out


def test_render_briefing_html_returns_none_when_empty(db_session):
    assert render_briefing_html("2026-05-15") is None


def test_render_briefing_html_includes_category(db_session):
    db_session.add(
        DailyBriefing(
            date="2026-05-15",
            category="テクノロジー",
            content="1. **記事タイトル**\n   要約\n   🔗 https://example.com/a",
        )
    )
    db_session.commit()

    html = render_briefing_html("2026-05-15")
    assert html is not None
    assert "テクノロジー" in html
    assert "<b>記事タイトル</b>" in html
    assert '<a href="https://example.com/a">' in html
