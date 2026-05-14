from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .core.config import settings
from .core.database import engine, Base
from .api import articles_router, briefings_router, stats_router, system_router
from .services.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asayomi API",
    description="朝読み - 日本ニュース自動収集・分析システム",
    version="0.1.0",
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


@app.on_event("startup")
async def startup():
    start_scheduler()


@app.on_event("shutdown")
async def shutdown():
    stop_scheduler()


@app.get("/")
async def root():
    return {"message": "Asayomi API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
