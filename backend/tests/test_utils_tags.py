"""Tag normalize/parse helpers — small but used everywhere tags are
read or written, so lock them down."""
from app.utils.tags import normalize_tag_string, parse_tags


def test_normalize_strips_whitespace():
    assert normalize_tag_string("AI, 半導体 ,日本") == "AI,半導体,日本"


def test_normalize_drops_empties():
    assert normalize_tag_string(",,a,,,b,") == "a,b"


def test_normalize_handles_none_and_empty():
    assert normalize_tag_string(None) == ""
    assert normalize_tag_string("") == ""
    assert normalize_tag_string("   ") == ""


def test_parse_returns_list():
    assert parse_tags("AI,半導体,日本") == ["AI", "半導体", "日本"]


def test_parse_strips_legacy_unnormalized_data():
    assert parse_tags("a, b , c,") == ["a", "b", "c"]


def test_parse_empty_to_empty_list():
    assert parse_tags(None) == []
    assert parse_tags("") == []
