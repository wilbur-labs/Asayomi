"""APScheduler ベースのタスクスケジューラ"""
import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.article import Article
from .ai_processor import process_unprocessed
from .briefing import (
    generate_briefing,
    generate_monthly_briefing,
    generate_weekly_briefing,
)
from .data_collector import collect_all
from .dedupe import detect_duplicates
from .notify import send_daily_briefing_notifications

logger = logging.getLogger(__name__)


def job_collect_and_process():
    """定期収集 → 重複検知 → AI処理 → ブリーフィング"""
    logger.info("===== 定期タスク開始 =====")
    collect_all(fetch_fulltext=True)
    detect_duplicates()
    process_unprocessed(limit=50)
    generate_briefing()
    logger.info("===== 定期タスク完了 =====")


def job_daily_notify():
    """毎朝 6:00 に通知送信"""
    send_daily_briefing_notifications()


def job_weekly():
    generate_weekly_briefing()


def job_monthly():
    generate_monthly_briefing()


def job_cleanup():
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
    scheduler.add_job(job_daily_notify, "cron", hour=6, minute=0, id="daily_notify")
    scheduler.add_job(job_weekly, "cron", day_of_week="mon", hour=7, minute=0, id="weekly")
    scheduler.add_job(job_monthly, "cron", day=1, hour=7, minute=30, id="monthly")
    scheduler.add_job(job_cleanup, "cron", hour=3, minute=0, id="cleanup")
    scheduler.start()
    logger.info(f"スケジューラ起動（収集間隔: {settings.collection_interval_hours}時間）")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("スケジューラ停止")
