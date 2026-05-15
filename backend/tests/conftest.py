"""Shared test fixtures.

Why this conftest is non-trivial:
- `app.main` runs `Base.metadata.create_all(bind=engine)` at import time and
  starts a scheduler in its lifespan, both against the real SQLite file.
- Several services capture `SessionLocal` at *their* module import time
  (`from ..core.database import SessionLocal`).

So we must:
1. Set safe env vars (empty Azure keys → no real API client gets built).
2. Override `app.core.database.engine` and `SessionLocal` to point at an
   in-memory SQLite **before** `app.main` is imported.
3. Use `StaticPool` so every connection sees the same in-memory database
   (default SQLite in-memory is per-connection).
4. Use `TestClient(app)` *without* the `with` context manager so the
   FastAPI lifespan (scheduler / FTS5 init) does not fire during tests.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "")

import sys
from pathlib import Path

# Allow `import app...` from the backend root
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import database module FIRST so we can override its attributes before
# any other app module captures them.
from app.core import database as _db_mod

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

_db_mod.engine = _test_engine
_db_mod.SessionLocal = _TestSessionLocal

# Now safe to import the app — `Base.metadata.create_all(bind=engine)` will
# create tables on the test engine.
from app.core.database import Base  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_tables():
    """Truncate all tables before each test — cheap on in-memory SQLite."""
    Base.metadata.create_all(bind=_test_engine)
    with _test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield


@pytest.fixture
def db_session():
    """Direct SQLAlchemy session for tests that need to seed/inspect data."""
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """FastAPI test client. No `with` → lifespan does NOT run, so the
    scheduler and FTS5 init stay out of the test process."""
    return TestClient(app)


# ----- Mock Azure OpenAI -----


class _MockMessage:
    def __init__(self, content):
        self.content = content


class _MockChoice:
    def __init__(self, content):
        self.message = _MockMessage(content)


class _MockUsage:
    prompt_tokens = 100
    completion_tokens = 50


class _MockResponse:
    def __init__(self, content):
        self.choices = [_MockChoice(content)]
        self.usage = _MockUsage()


class MockAzureClient:
    """Mimics the slice of the AzureOpenAI client surface our code uses:
    `client.chat.completions.create(...)` returning an object with
    `.choices[0].message.content` and `.usage`.
    """

    def __init__(self, content: str):
        self._content = content
        self.chat = self
        self.completions = self
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _MockResponse(self._content)


@pytest.fixture
def mock_openai_client():
    """Factory: build a MockAzureClient with a JSON payload string."""
    def _make(content: str) -> MockAzureClient:
        return MockAzureClient(content)
    return _make
