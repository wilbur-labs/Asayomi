from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..models.article import Article

router = APIRouter(prefix="/api/v1/articles", tags=["articles"])


@router.get("")
def list_articles(
    category: Optional[str] = None,
    source: Optional[str] = None,
    include_duplicates: bool = False,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Article)
    if not include_duplicates:
        q = q.filter(Article.is_duplicate == False)
    if category:
        q = q.filter(Article.category == category)
    if source:
        q = q.filter(Article.source == source)
    total = q.count()
    articles = (
        q.order_by(Article.importance_score.desc(), Article.collected_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"total": total, "articles": [_serialize(a) for a in articles]}


@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    return _serialize(article, include_full=True)


def _serialize(a: Article, include_full: bool = False) -> dict:
    data = {
        "id": a.id,
        "title": a.title,
        "original_title": a.original_title,
        "url": a.url,
        "source": a.source,
        "language": a.language,
        "category": a.category,
        "summary": a.summary,
        "importance_score": a.importance_score,
        "tags": a.tags.split(",") if a.tags else [],
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "collected_at": a.collected_at.isoformat() if a.collected_at else None,
        "is_favorite": a.is_favorite,
        "is_read": a.is_read,
    }
    if include_full:
        data["full_content"] = a.full_content
        data["original_content"] = a.original_content
    return data
