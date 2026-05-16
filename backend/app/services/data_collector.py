"""RSS データ収集サービス"""
import logging
from datetime import datetime, timezone
from calendar import timegm

import feedparser
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.article import Article
from ..models.source import Source
from .fulltext import fetch_full_text

logger = logging.getLogger(__name__)


def parse_published(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(timegm(entry.published_parsed), tz=timezone.utc)
    return None


def collect_from_source(db: Session, source: Source, fetch_fulltext: bool = False) -> int:
    """1つのRSSソースからデータを収集"""
    if not source.enabled:
        return 0
    try:
        feed = feedparser.parse(source.url)
        count = 0
        for entry in feed.entries[:30]:
            url = entry.get("link", "")
            if not url:
                continue
            if db.query(Article).filter(Article.url == url).first():
                continue

            title = entry.get("title", "")
            full_text = None
            if fetch_fulltext:
                full_text = fetch_full_text(url)

            article = Article(
                title=title,
                original_title=title,
                url=url,
                source=source.name,
                category=source.category,
                language=source.language,
                original_content=entry.get("summary", ""),
                full_content=full_text,
                published_at=parse_published(entry),
                collected_at=datetime.now(timezone.utc),
            )
            db.add(article)
            count += 1
        db.commit()
        logger.info(f"[{source.name}] {count} 件収集")
        return count
    except Exception as e:
        logger.error(f"[{source.name}] 収集エラー: {e}")
        db.rollback()
        return 0


def collect_all(fetch_fulltext: bool = True) -> int:
    """全ソースからデータを収集（DB の sources テーブルを参照）"""
    db = SessionLocal()
    total = 0
    try:
        sources = db.query(Source).filter(Source.enabled == True).all()
        for source in sources:
            total += collect_from_source(db, source, fetch_fulltext=fetch_fulltext)
        logger.info(f"収集完了: 合計 {total} 件 ({len(sources)} ソース)")
    finally:
        db.close()
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collect_all()
