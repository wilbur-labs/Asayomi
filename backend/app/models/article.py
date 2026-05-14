from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from datetime import datetime, timezone
from ..core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    category = Column(String(50), default="総合")
    summary = Column(Text)
    original_content = Column(Text)
    translated_title = Column(String(500))  # 英文→日語翻訳用
    importance_score = Column(Float, default=0.0)
    tags = Column(String(500))
    published_at = Column(DateTime)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed = Column(Boolean, default=False)


class DailyBriefing(Base):
    __tablename__ = "daily_briefings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
