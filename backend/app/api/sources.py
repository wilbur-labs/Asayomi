from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import Depends

from ..core.database import get_db
from ..models.article import Article
from ..services.sources import RSS_SOURCES

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


class SourceToggle(BaseModel):
    enabled: bool


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    """ソース一覧 + 各ソースの記事数 / 最新収集時刻"""
    counts = dict(
        db.query(Article.source, func.count(Article.id)).group_by(Article.source).all()
    )
    latest = dict(
        db.query(Article.source, func.max(Article.collected_at)).group_by(Article.source).all()
    )
    result = []
    for s in RSS_SOURCES:
        result.append({
            "name": s["name"],
            "url": s["url"],
            "category": s["category"],
            "language": s.get("language", "ja"),
            "enabled": s.get("enabled", True),
            "count": counts.get(s["name"], 0),
            "latest_collected_at": latest.get(s["name"]).isoformat() if latest.get(s["name"]) else None,
        })
    return {"sources": result}


@router.post("/{name}/toggle")
def toggle_source(name: str, body: SourceToggle):
    """ソースの有効/無効を切替（メモリ上のみ。再起動でリセット）"""
    for s in RSS_SOURCES:
        if s["name"] == name:
            s["enabled"] = body.enabled
            return {"name": name, "enabled": body.enabled}
    raise HTTPException(status_code=404, detail=f"ソースが見つかりません: {name}")
