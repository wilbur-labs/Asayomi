from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..core.database import get_db
from ..models.article import DailyBriefing

router = APIRouter(prefix="/api/v1/briefings", tags=["briefings"])


@router.get("")
def list_briefings(
    date: str = None,
    db: Session = Depends(get_db),
):
    if not date:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    briefings = db.query(DailyBriefing).filter(DailyBriefing.date == date).all()
    return {
        "date": date,
        "briefings": [
            {"id": b.id, "category": b.category, "content": b.content}
            for b in briefings
        ],
    }
