"""Tag string helpers.

Article.tags is stored as a comma-separated `String(500)`. These helpers
keep that representation canonical — strip whitespace per tag, drop empties —
so a future move to a proper Tag table doesn't have to deal with stray
spaces or `",,a,,b"` style inputs.
"""
from typing import Optional


def normalize_tag_string(raw: Optional[str]) -> str:
    """Canonicalize a comma-separated tag string for DB storage."""
    if not raw:
        return ""
    return ",".join(t.strip() for t in raw.split(",") if t.strip())


def parse_tags(raw: Optional[str]) -> list[str]:
    """Parse a DB-stored tag string into a list, applying the same
    normalization at read time so legacy un-normalized rows still
    surface clean tags to the API."""
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]
