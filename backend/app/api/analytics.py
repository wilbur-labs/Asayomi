"""分析・エクスポート・用量・チャット系 API"""
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
from io import StringIO
import csv
import json

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.article import Article
from ..models.api_usage import ApiUsage

router = APIRouter(prefix="/api/v1", tags=["analytics"])


# ----- トレンド分析 -----
@router.get("/trends/tags")
def trending_tags(days: int = 7, limit: int = 20, db: Session = Depends(get_db)):
    """直近 N 日のタグ頻度"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(Article.tags)
        .filter(Article.collected_at >= cutoff, Article.tags.isnot(None), Article.tags != "")
        .all()
    )
    counter = Counter()
    for (tags_str,) in rows:
        for t in (tags_str or "").split(","):
            t = t.strip()
            if t:
                counter[t] += 1
    return {
        "days": days,
        "tags": [{"tag": t, "count": c} for t, c in counter.most_common(limit)],
    }


@router.get("/trends/timeline")
def trending_timeline(days: int = 14, db: Session = Depends(get_db)):
    """日別・カテゴリ別の記事数推移"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(Article.collected_at).label("d"),
            Article.category,
            func.count(Article.id),
        )
        .filter(Article.collected_at >= cutoff, Article.is_duplicate == False)
        .group_by("d", Article.category)
        .all()
    )
    timeline = defaultdict(lambda: defaultdict(int))
    for d, cat, c in rows:
        timeline[str(d)][cat] = c
    return {
        "days": days,
        "timeline": [{"date": d, **counts} for d, counts in sorted(timeline.items())],
    }


# ----- API 用量 -----
@router.get("/usage")
def api_usage_summary(days: int = 30, db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(ApiUsage).filter(ApiUsage.timestamp >= cutoff).all()
    by_op = defaultdict(lambda: {"count": 0, "tokens": 0, "cost": 0.0})
    for u in rows:
        by_op[u.operation]["count"] += 1
        by_op[u.operation]["tokens"] += u.total_tokens or 0
        by_op[u.operation]["cost"] += u.estimated_cost_usd or 0.0
    total_tokens = sum(b["tokens"] for b in by_op.values())
    total_cost = sum(b["cost"] for b in by_op.values())
    return {
        "days": days,
        "total_calls": len(rows),
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 4),
        "by_operation": {k: {**v, "cost": round(v["cost"], 4)} for k, v in by_op.items()},
    }


# ----- エクスポート -----
@router.get("/export/articles.json")
def export_json(
    days: int = 30,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(Article).filter(Article.collected_at >= cutoff)
    if category:
        q = q.filter(Article.category == category)
    items = []
    for a in q.all():
        items.append({
            "id": a.id, "title": a.title, "url": a.url, "source": a.source,
            "language": a.language, "category": a.category, "summary": a.summary,
            "tags": a.tags, "importance_score": a.importance_score,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "collected_at": a.collected_at.isoformat() if a.collected_at else None,
        })
    payload = json.dumps({"exported_at": datetime.now(timezone.utc).isoformat(), "count": len(items), "articles": items}, ensure_ascii=False, indent=2)
    return Response(content=payload, media_type="application/json",
                    headers={"Content-Disposition": "attachment; filename=articles.json"})


@router.get("/export/articles.csv")
def export_csv(days: int = 30, category: str | None = None, db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(Article).filter(Article.collected_at >= cutoff)
    if category:
        q = q.filter(Article.category == category)
    sio = StringIO()
    w = csv.writer(sio)
    w.writerow(["id", "title", "url", "source", "language", "category", "summary",
                "tags", "importance_score", "published_at", "collected_at"])
    for a in q.all():
        w.writerow([
            a.id, a.title, a.url, a.source, a.language, a.category,
            a.summary or "", a.tags or "", a.importance_score,
            a.published_at.isoformat() if a.published_at else "",
            a.collected_at.isoformat() if a.collected_at else "",
        ])
    return Response(content=sio.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=articles.csv"})


# ----- AI チャット -----
class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat_endpoint(body: ChatRequest):
    from ..services.chat import chat
    return chat(body.question)
