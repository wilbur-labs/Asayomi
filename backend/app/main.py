from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .core.config import settings
from .core.database import engine, Base
from .core.security import require_admin_token
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

Base.metadata.create_all(bind=engine)

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
# /system/* endpoints can spend Azure OpenAI tokens, hammer external RSS,
# and fire notifications — gate behind ADMIN_TOKEN via shared-secret header.
app.include_router(system_router, dependencies=[Depends(require_admin_token)])
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
