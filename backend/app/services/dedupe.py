"""記事重複検知サービス（タイトル類似度ベース）"""
import logging
import re
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.article import Article

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.75   # この閾値以上で重複と判定
WINDOW_HOURS = 48              # 比較対象は直近 N 時間以内


def _normalize(title: str) -> str:
    """比較用にタイトルを正規化"""
    title = title.lower()
    # 全角記号 → 半角、句読点除去
    title = re.sub(r"[【】「」『』（）\[\]\(\)。、,．・,!?！？:：…—\-\s]+", " ", title)
    return title.strip()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def detect_duplicates(window_hours: int = WINDOW_HOURS) -> int:
    """直近 N 時間内の記事間で重複を検知。重複したものに is_duplicate=True を付与。"""
    db: Session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        articles = (
            db.query(Article)
            .filter(Article.collected_at >= cutoff, Article.is_duplicate == False)
            .order_by(Article.collected_at.asc())  # 古い方を「元」にする
            .all()
        )
        marked = 0
        for i, target in enumerate(articles):
            if target.is_duplicate:
                continue
            for prev in articles[:i]:
                if prev.is_duplicate:
                    continue
                # 自分のソースと同じならスキップ（同じソース内での再投稿は無視）
                if prev.source == target.source:
                    continue
                sim = _similarity(prev.title, target.title)
                if sim >= SIMILARITY_THRESHOLD:
                    target.is_duplicate = True
                    target.duplicate_of_id = prev.id
                    marked += 1
                    logger.info(
                        f"重複検知 [{sim:.2f}] {target.source}「{target.title[:30]}」"
                        f" ← {prev.source}「{prev.title[:30]}」"
                    )
                    break
        db.commit()
        logger.info(f"重複検知完了: {marked} 件マーク")
        return marked
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detect_duplicates()
