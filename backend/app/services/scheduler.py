"""APScheduler ベースのタスクスケジューラ"""
import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.article import Article

logger = logging.getLogger(__name__)


def job_collect_and_process():
    """定期収集 → 重複検知 → AI処理 → ブリーフィング"""
    from .data_collector import collect_all
    from .dedupe import detect_duplicates
    from .ai_processor import process_unprocessed
    from .briefing import generate_briefing

    logger.info("===== 定期タスク開始 =====")
    collect_all(fetch_fulltext=True)
    detect_duplicates()
    process_unprocessed(limit=50)
    generate_briefing()
    logger.info("===== 定期タスク完了 =====")


def job_cleanup():
    """古いデータを削除（お気に入り除外）"""
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.data_retention_days)
        deleted = (
            db.query(Article)
            .filter(Article.collected_at < cutoff, Article.is_favorite == False)
            .delete()
        )
        db.commit()
        logger.info(f"クリーンアップ: {deleted} 件削除")
    finally:
        db.close()


scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        job_collect_and_process,
        "interval",
        hours=settings.collection_interval_hours,
        id="collect",
    )
    scheduler.add_job(job_cleanup, "cron", hour=3, minute=0, id="cleanup")
    scheduler.start()
    logger.info(f"スケジューラ起動（収集間隔: {settings.collection_interval_hours}時間）")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("スケジューラ停止")
