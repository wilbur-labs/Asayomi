"""ニュースソースの初期値 + DB シード関数。

実行時のソース一覧は `models.source.Source` テーブルに永続化される。
このモジュールは「初回起動時のデフォルト値」のみを提供する。
"""
from sqlalchemy.orm import Session

from ..models.source import Source


DEFAULT_SOURCES: list[dict] = [
    # --- 日本語ソース ---
    {
        "name": "NHK News Web",
        "url": "https://www.nhk.or.jp/rss/news/cat0.xml",
        "category": "総合",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "Yahoo!ニュース",
        "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
        "category": "総合",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "ITmedia",
        "url": "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml",
        "category": "テクノロジー",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "Gigazine",
        "url": "https://gigazine.net/news/rss_2.0/",
        "category": "テクノロジー",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "東洋経済オンライン",
        "url": "https://toyokeizai.net/list/feed/rss",
        "category": "経済・ビジネス",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "BBC News Japan",
        "url": "https://feeds.bbci.co.uk/japanese/rss.xml",
        "category": "国際",
        "language": "ja",
        "enabled": True,
    },
    # --- 英語ソース（AI で日本語に翻訳） ---
    {
        "name": "The Japan Times",
        "url": "https://www.japantimes.co.jp/feed/",
        "category": "国際",
        "language": "en",
        "enabled": True,
    },
    {
        "name": "Yomiuri English",
        "url": "https://japannews.yomiuri.co.jp/feed/",
        "category": "国際",
        "language": "en",
        "enabled": True,
    },
]


def seed_sources_if_empty(db: Session) -> int:
    """sources テーブルが空のときだけ DEFAULT_SOURCES から初期化する。

    既存の運用 DB を壊さないため、空でなければ no-op。新しいデフォルト
    ソースを追加する運用ジョブは別途用意してね。
    """
    if db.query(Source).count() > 0:
        return 0
    for entry in DEFAULT_SOURCES:
        db.add(Source(**entry))
    db.commit()
    return len(DEFAULT_SOURCES)
