"""毎日ブリーフィング生成サービス"""
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.article import Article, DailyBriefing

logger = logging.getLogger(__name__)
CATEGORIES = ["総合", "テクノロジー", "経済・ビジネス", "国際"]


def generate_briefing(date_str: str = None) -> int:
    """指定日のブリーフィングを生成（デフォルト: 今日）"""
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    db = SessionLocal()
    try:
        # 当日の記事を取得
        start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        count = 0
        for cat in CATEGORIES:
            articles = (
                db.query(Article)
                .filter(
                    Article.collected_at >= start,
                    Article.collected_at < end,
                    Article.category == cat,
                    Article.processed == True,
                )
                .order_by(Article.importance_score.desc())
                .limit(5)
                .all()
            )
            if not articles:
                continue

            # 既存のブリーフィングを削除して再生成
            db.query(DailyBriefing).filter(
                DailyBriefing.date == date_str, DailyBriefing.category == cat
            ).delete()

            lines = [f"## {cat}（{date_str}）\n"]
            for i, a in enumerate(articles, 1):
                score = f"[{a.importance_score:.0f}/10]" if a.importance_score else ""
                lines.append(f"{i}. **{a.title}** {score}")
                if a.summary:
                    lines.append(f"   {a.summary}")
                lines.append(f"   🔗 {a.url}\n")

            briefing = DailyBriefing(
                date=date_str, category=cat, content="\n".join(lines)
            )
            db.add(briefing)
            count += 1

        db.commit()
        logger.info(f"ブリーフィング生成完了: {date_str} ({count} カテゴリ)")
        return count
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_briefing()
