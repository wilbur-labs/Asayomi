from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, Index
from datetime import datetime, timezone
from ..core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)  # 表示用（翻訳後）
    original_title = Column(String(500))          # 原語タイトル（翻訳前）
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    language = Column(String(10), default="ja")   # ja / en
    category = Column(String(50), default="総合")
    summary = Column(Text)                         # AI 要約（日本語）
    original_content = Column(Text)                # RSS の本文（短縮版）
    full_content = Column(Text)                    # 全文抓取結果
    importance_score = Column(Float, default=0.0)
    tags = Column(String(500))
    published_at = Column(DateTime)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    processed = Column(Boolean, default=False, index=True)
    is_duplicate = Column(Boolean, default=False, index=True)  # 重複検知
    duplicate_of_id = Column(Integer)               # 重複元の記事 ID
    is_favorite = Column(Boolean, default=False, index=True)
    is_read = Column(Boolean, default=False, index=True)


class DailyBriefing(Base):
    __tablename__ = "daily_briefings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# 全文検索インデックス（FTS5 は別途作成）
Index("idx_articles_collected_processed", Article.collected_at, Article.processed)
