from sqlalchemy import Boolean, Column, Integer, String

from ..core.database import Base


class Source(Base):
    """Persisted RSS / news source. Replaces the in-memory `RSS_SOURCES`
    list — toggling enabled/disabled now survives container restarts."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    url = Column(String(1000), nullable=False)
    category = Column(String(50), nullable=False)
    language = Column(String(10), default="ja", nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
