"""ブリーフィング生成サービス（日次・週次・月次）"""
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.article import Article, DailyBriefing

logger = logging.getLogger(__name__)
CATEGORIES = ["総合", "テクノロジー", "経済・ビジネス", "国際"]


def _build_lines(articles, header: str) -> str:
    lines = [header]
    for i, a in enumerate(articles, 1):
        score = f"[{a.importance_score:.0f}/10]" if a.importance_score else ""
        lines.append(f"{i}. **{a.title}** {score}")
        if a.summary:
            lines.append(f"   {a.summary}")
        lines.append(f"   🔗 {a.url}\n")
    return "\n".join(lines)


def generate_briefing(date_str: str = None) -> int:
    """指定日のブリーフィングを生成（デフォルト: 今日）"""
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    db = SessionLocal()
    try:
        start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        return _generate_for_window(db, date_str, start, end, top_n=5)
    finally:
        db.close()


def generate_weekly_briefing(end_date: str = None) -> int:
    """直近 7 日間の週次まとめ"""
    if not end_date:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
    start = end - timedelta(days=7)
    label = f"weekly-{end_date}"
    db = SessionLocal()
    try:
        return _generate_for_window(db, label, start, end, top_n=10)
    finally:
        db.close()


def generate_monthly_briefing(month: str = None) -> int:
    """月次まとめ（month=YYYY-MM）"""
    if not month:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
    start = datetime.strptime(month + "-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    label = f"monthly-{month}"
    db = SessionLocal()
    try:
        return _generate_for_window(db, label, start, end, top_n=15)
    finally:
        db.close()


def _generate_for_window(
    db: Session, label: str, start: datetime, end: datetime, top_n: int
) -> int:
    count = 0
    for cat in CATEGORIES:
        articles = (
            db.query(Article)
            .filter(
                Article.collected_at >= start,
                Article.collected_at < end,
                Article.category == cat,
                Article.processed == True,
                Article.is_duplicate == False,
            )
            .order_by(Article.importance_score.desc())
            .limit(top_n)
            .all()
        )
        if not articles:
            continue
        db.query(DailyBriefing).filter(
            DailyBriefing.date == label, DailyBriefing.category == cat
        ).delete()
        content = _build_lines(articles, f"## {cat}（{label}）\n")
        db.add(DailyBriefing(date=label, category=cat, content=content))
        count += 1
    db.commit()
    logger.info(f"ブリーフィング [{label}] 生成完了: {count} カテゴリ")
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_briefing()
