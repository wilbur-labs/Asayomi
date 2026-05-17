from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .core.config import settings
from .core.database import engine, Base
from .api import (
    articles_router,
    briefings_router,
    stats_router,
    system_router,
    user_actions_router,
    search_router,
    sources_router,
    feed_router,
    analytics_router,
)
from .services.scheduler import start_scheduler, stop_scheduler
from .services.search import init_fts5
from sqlalchemy import text, inspect


def _auto_migrate() -> None:
    """既存 SQLite テーブルに対する軽量カラム追加マイグレーション。"""
    insp = inspect(engine)
    if "articles" not in insp.get_table_names():
        return
    existing_cols = {c["name"] for c in insp.get_columns("articles")}
    additions = [
        ("image_url", "VARCHAR(1000)"),
        ("key_points", "TEXT"),
    ]
    with engine.begin() as conn:
        for name, ddl in additions:
            if name not in existing_cols:
                conn.execute(text(f"ALTER TABLE articles ADD COLUMN {name} {ddl}"))


Base.metadata.create_all(bind=engine)
_auto_migrate()

app = FastAPI(
    title="Asayomi API",
    description="Asayomi - Japan News Briefing System",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles_router)
app.include_router(briefings_router)
app.include_router(stats_router)
app.include_router(system_router)
app.include_router(user_actions_router)
app.include_router(search_router)
app.include_router(sources_router)
app.include_router(feed_router)
app.include_router(analytics_router)


@app.on_event("startup")
async def startup():
    init_fts5()
    start_scheduler()


@app.on_event("shutdown")
async def shutdown():
    stop_scheduler()


@app.get("/")
async def root():
    return {"message": "Asayomi API", "version": "0.2.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
