from fastapi import APIRouter
import logging

router = APIRouter(prefix="/api/v1/system", tags=["system"])
logger = logging.getLogger(__name__)


@router.post("/collect")
def trigger_collect(fulltext: bool = True):
    from ..services.data_collector import collect_all
    count = collect_all(fetch_fulltext=fulltext)
    return {"message": f"収集完了: {count} 件"}


@router.post("/dedupe")
def trigger_dedupe():
    from ..services.dedupe import detect_duplicates
    count = detect_duplicates()
    return {"message": f"重複検知完了: {count} 件マーク"}


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


@router.post("/run-all")
def trigger_run_all():
    """全パイプラインを実行: 収集 → 重複検知 → AI処理 → ブリーフィング"""
    from ..services.scheduler import job_collect_and_process
    job_collect_and_process()
    return {"message": "全パイプライン実行完了"}
