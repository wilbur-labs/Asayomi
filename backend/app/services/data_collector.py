"""RSS データ収集サービス"""
import logging
from datetime import datetime, timezone
from typing import List

import feedparser
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.article import Article
from .sources import RSS_SOURCES

logger = logging.getLogger(__name__)


def parse_published(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        from calendar import timegm
        return datetime.fromtimestamp(timegm(entry.published_parsed), tz=timezone.utc)
    return None


def collect_from_source(db: Session, source: dict) -> int:
    """1つのRSSソースからデータを収集"""
    try:
        feed = feedparser.parse(source["url"])
        count = 0
        for entry in feed.entries[:30]:
            url = entry.get("link", "")
            if not url or db.query(Article).filter(Article.url == url).first():
                continue
            article = Article(
                title=entry.get("title", ""),
                url=url,
                source=source["name"],
                category=source["category"],
                original_content=entry.get("summary", ""),
                published_at=parse_published(entry),
                collected_at=datetime.now(timezone.utc),
            )
            db.add(article)
            count += 1
        db.commit()
        logger.info(f"[{source['name']}] {count} 件収集")
        return count
    except Exception as e:
        logger.error(f"[{source['name']}] 収集エラー: {e}")
        db.rollback()
        return 0


def collect_all() -> int:
    """全ソースからデータを収集"""
    db = SessionLocal()
    total = 0
    try:
        for source in RSS_SOURCES:
            total += collect_from_source(db, source)
        logger.info(f"収集完了: 合計 {total} 件")
    finally:
        db.close()
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collect_all()
