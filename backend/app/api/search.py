from fastapi import APIRouter, Query

from ..services.search import search_articles

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
def search(q: str = Query(..., min_length=1), limit: int = Query(50, le=200)):
    results = search_articles(q, limit=limit)
    return {"query": q, "total": len(results), "articles": results}
