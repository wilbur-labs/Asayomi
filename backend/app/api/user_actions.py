from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.article import Article

router = APIRouter(prefix="/api/v1/articles", tags=["user-actions"])


@router.post("/{article_id}/favorite")
def toggle_favorite(article_id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    a.is_favorite = not a.is_favorite
    db.commit()
    return {"id": a.id, "is_favorite": a.is_favorite}


@router.post("/{article_id}/read")
def mark_read(article_id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    a.is_read = True
    db.commit()
    return {"id": a.id, "is_read": True}


@router.post("/{article_id}/unread")
def mark_unread(article_id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    a.is_read = False
    db.commit()
    return {"id": a.id, "is_read": False}
