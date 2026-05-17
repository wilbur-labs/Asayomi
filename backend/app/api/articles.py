import json
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional

from ..core.database import get_db
from ..models.article import Article

router = APIRouter(prefix="/api/v1/articles", tags=["articles"])


@router.get("")
def list_articles(
    category: Optional[str] = None,
    source: Optional[str] = None,
    favorite_only: bool = False,
    unread_only: bool = False,
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
    if favorite_only:
        q = q.filter(Article.is_favorite == True)
    if unread_only:
        q = q.filter(Article.is_read == False)
    total = q.count()
    articles = (
        q.order_by(Article.importance_score.desc(), Article.collected_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    # 重複サイバー（同じ事件をマークした他ソース）件数を埋める
    serialized = [_serialize(a) for a in articles]
    if articles and not include_duplicates:
        ids = [a.id for a in articles]
        sib_rows = (
            db.query(Article.duplicate_of_id, Article.source)
            .filter(Article.duplicate_of_id.in_(ids), Article.is_duplicate == True)
            .all()
        )
        sibling_map: dict[int, list[str]] = {}
        for parent_id, src in sib_rows:
            sibling_map.setdefault(parent_id, []).append(src)
        for item in serialized:
            sources = sibling_map.get(item["id"], [])
            item["sibling_count"] = len(sources)
            item["sibling_sources"] = sources
    return {"total": total, "articles": serialized}


@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    data = _serialize(article, include_full=True)
    # 同じ事件の他ソース
    siblings = (
        db.query(Article)
        .filter(Article.duplicate_of_id == article.id, Article.is_duplicate == True)
        .all()
    )
    data["siblings"] = [
        {"id": s.id, "title": s.title, "source": s.source, "url": s.url}
        for s in siblings
    ]
    return data


@router.get("/{article_id}/related")
def related_articles(
    article_id: int,
    limit: int = Query(default=5, le=20),
    db: Session = Depends(get_db),
):
    """同カテゴリ + タグ重複度で関連記事を返す。"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="記事が見つかりません")

    own_tags = [t for t in (article.tags or "").split(",") if t.strip()]
    q = db.query(Article).filter(
        Article.id != article_id,
        Article.is_duplicate == False,
    )
    # 候補プールを広めに取る（同カテゴリ優先、足りなければ他カテゴリも）
    same_cat = q.filter(Article.category == article.category).order_by(
        Article.importance_score.desc(), Article.collected_at.desc()
    ).limit(50).all()

    def overlap_score(a: Article) -> tuple[int, float]:
        a_tags = [t for t in (a.tags or "").split(",") if t.strip()]
        overlap = len(set(own_tags) & set(a_tags))
        return (overlap, a.importance_score or 0.0)

    same_cat.sort(key=overlap_score, reverse=True)
    picks = same_cat[:limit]
    return {"related": [_serialize(p) for p in picks]}


def _serialize(a: Article, include_full: bool = False) -> dict:
    kp_list: list[str] = []
    if a.key_points:
        try:
            parsed = json.loads(a.key_points)
            if isinstance(parsed, list):
                kp_list = [str(x) for x in parsed]
        except Exception:
            kp_list = []
    body_for_reading = a.full_content or a.summary or a.original_content or ""
    # 日本語の読書時間: 約 500 文字/分
    reading_minutes = max(1, round(len(body_for_reading) / 500))
    data = {
        "id": a.id,
        "title": a.title,
        "original_title": a.original_title,
        "url": a.url,
        "source": a.source,
        "language": a.language,
        "category": a.category,
        "summary": a.summary,
        "key_points": kp_list,
        "importance_score": a.importance_score,
        "tags": a.tags.split(",") if a.tags else [],
        "image_url": a.image_url,
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "collected_at": a.collected_at.isoformat() if a.collected_at else None,
        "is_favorite": a.is_favorite,
        "is_read": a.is_read,
        "reading_minutes": reading_minutes,
    }
    if include_full:
        data["full_content"] = a.full_content
        data["original_content"] = a.original_content
    return data
