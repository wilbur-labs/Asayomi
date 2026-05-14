from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..models.article import Article

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Article).count()
    processed = db.query(Article).filter(Article.processed == True).count()
    by_category = (
        db.query(Article.category, func.count(Article.id))
        .filter(Article.processed == True)
        .group_by(Article.category)
        .all()
    )
    by_source = (
        db.query(Article.source, func.count(Article.id))
        .group_by(Article.source)
        .all()
    )
    return {
        "total": total,
        "processed": processed,
        "unprocessed": total - processed,
        "by_category": {cat: cnt for cat, cnt in by_category},
        "by_source": {src: cnt for src, cnt in by_source},
    }
