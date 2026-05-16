from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.article import Article
from ..models.source import Source

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


class SourceToggle(BaseModel):
    enabled: bool


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    """ソース一覧 + 各ソースの記事数 / 最新収集時刻。

    sources テーブルが空（マイグレーション直後など）の場合は空リストを返す。
    アプリ起動時に services.sources.seed_sources_if_empty() でデフォルト値が
    投入される想定。
    """
    counts = dict(
        db.query(Article.source, func.count(Article.id)).group_by(Article.source).all()
    )
    latest = dict(
        db.query(Article.source, func.max(Article.collected_at)).group_by(Article.source).all()
    )
    sources = db.query(Source).order_by(Source.id).all()
    result = [
        {
            "name": s.name,
            "url": s.url,
            "category": s.category,
            "language": s.language,
            "enabled": s.enabled,
            "count": counts.get(s.name, 0),
            "latest_collected_at": latest.get(s.name).isoformat() if latest.get(s.name) else None,
        }
        for s in sources
    ]
    return {"sources": result}


@router.post("/{name}/toggle")
def toggle_source(name: str, body: SourceToggle, db: Session = Depends(get_db)):
    """ソースの有効 / 無効を切替。DB に永続化されるので再起動でも消えない。"""
    s = db.query(Source).filter(Source.name == name).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"ソースが見つかりません: {name}")
    s.enabled = body.enabled
    db.commit()
    return {"name": name, "enabled": body.enabled}
