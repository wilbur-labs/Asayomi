"""SQLite 全文検索（FTS5 + LIKE ハイブリッド）"""
import logging
import re
from sqlalchemy import text, or_
from ..core.database import engine, SessionLocal
from ..models.article import Article

logger = logging.getLogger(__name__)


def init_fts5() -> None:
    with engine.begin() as conn:
        try:
            conn.execute(text(
                "CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5("
                "title, summary, tags, source, content='articles', content_rowid='id', "
                "tokenize='unicode61')"
            ))
        except Exception as e:
            logger.warning(f"FTS5 利用不可: {e}")
            return
        conn.execute(text("INSERT INTO articles_fts(articles_fts) VALUES('rebuild')"))
        for trig_sql in [
            """CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
              INSERT INTO articles_fts(rowid, title, summary, tags, source)
              VALUES (new.id, new.title, COALESCE(new.summary,''), COALESCE(new.tags,''), new.source);
            END""",
            """CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
              INSERT INTO articles_fts(articles_fts, rowid, title, summary, tags, source)
              VALUES('delete', old.id, old.title, COALESCE(old.summary,''), COALESCE(old.tags,''), old.source);
            END""",
            """CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
              INSERT INTO articles_fts(articles_fts, rowid, title, summary, tags, source)
              VALUES('delete', old.id, old.title, COALESCE(old.summary,''), COALESCE(old.tags,''), old.source);
              INSERT INTO articles_fts(rowid, title, summary, tags, source)
              VALUES (new.id, new.title, COALESCE(new.summary,''), COALESCE(new.tags,''), new.source);
            END""",
        ]:
            conn.execute(text(trig_sql))
    logger.info("FTS5 初期化完了")


def _has_cjk(s: str) -> bool:
    return bool(re.search(r"[\u3000-\u9fff\u30a0-\u30ff\uff00-\uffef]", s))


def _serialize(a: Article) -> dict:
    return {
        "id": a.id, "title": a.title, "url": a.url, "source": a.source,
        "category": a.category, "summary": a.summary, "language": a.language,
        "importance_score": a.importance_score,
        "tags": a.tags.split(",") if a.tags else [],
        "image_url": a.image_url,
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "collected_at": a.collected_at.isoformat() if a.collected_at else None,
        "is_favorite": a.is_favorite, "is_read": a.is_read,
        "original_title": a.original_title,
    }


def search_articles(query: str, limit: int = 50) -> list[dict]:
    """ハイブリッド検索：CJK は LIKE、英数字は FTS5。空白区切りの複数語に対応。"""
    db = SessionLocal()
    try:
        terms = [t for t in query.split() if t]
        if not terms:
            return []

        q = db.query(Article).filter(Article.is_duplicate == False)

        # 各 term は AND（すべて含む）、フィールドは OR
        for term in terms:
            kw = f"%{term}%"
            q = q.filter(
                or_(
                    Article.title.like(kw),
                    Article.original_title.like(kw),
                    Article.summary.like(kw),
                    Article.tags.like(kw),
                )
            )

        rows = (
            q.order_by(Article.importance_score.desc(), Article.collected_at.desc())
            .limit(limit)
            .all()
        )
        return [_serialize(r) for r in rows]
    finally:
        db.close()
