from fastapi import APIRouter
import logging

router = APIRouter(prefix="/api/v1/system", tags=["system"])
logger = logging.getLogger(__name__)


@router.post("/collect")
def trigger_collect():
    from ..services.data_collector import collect_all
    count = collect_all()
    return {"message": f"収集完了: {count} 件"}


@router.post("/process")
def trigger_process():
    from ..services.ai_processor import process_unprocessed
    count = process_unprocessed(limit=50)
    return {"message": f"AI処理完了: {count} 件"}


@router.post("/briefing")
def trigger_briefing():
    from ..services.briefing import generate_briefing
    count = generate_briefing()
    return {"message": f"ブリーフィング生成完了: {count} カテゴリ"}
