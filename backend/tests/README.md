# Tests — Asayomi backend

The point of this suite is **not** coverage — it's a safety net for the
upcoming refactor batch laid out in the M1 audit report. Each test
locks in current behavior on a path that a planned refactor will touch.

## Run

```bash
# from repo root
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt -r backend/requirements-dev.txt

cd backend
pytest
```

## What's tested

| File | Why |
|---|---|
| `test_articles_api.py` | Pins the `tags: string[]` / category / pagination / duplicate-exclusion contract that frontend depends on. Touched by P1-3 (tags type) and P1-1 (ArticlesPage split). |
| `test_search.py` | LIKE-based hybrid search; touched by P1-3 (tags refactor) and any future FTS5 work. |
| `test_dedupe.py` | Title-similarity threshold + same-source skip rule. Hardcoded behavior people will be tempted to "improve" without realising. |
| `test_briefing.py` | Per-category grouping + filters (processed / not-duplicate). Touched by P1-9 (DailyBriefing.date refactor). |
| `test_notify_render.py` | HTML escape + markdown-lite for the email/webhook channels. Locks in the P0-5 fix. |
| `test_ai_processor.py` | JSON parsing + EN translation paths. Touched by P1-5 (nested try refactor). |

## Why so few

Anything outside this list either:
- has no planned refactor (don't preemptively test stable code), or
- needs design changes before it's worth testing (`scheduler.py`, `fulltext.py`'s
  external HTTP — would benefit from dependency injection first).

When a refactor PR moves into one of those areas, add coverage **in that PR**,
not here.

## Notes on the fixture setup

See `conftest.py` for the full story, but the gotchas are:

- The conftest overrides `app.core.database.engine` / `SessionLocal` **before**
  `app.main` is imported, otherwise `Base.metadata.create_all` runs against the
  real SQLite file.
- `TestClient(app)` is used **without** the `with` context manager so the
  FastAPI lifespan (APScheduler start, FTS5 init) does not fire in tests.
- `MockAzureClient` fakes only the slice of the OpenAI client surface our code
  uses; no real API call is ever made. Tests asserting `Azure OpenAI` behavior
  should always go through this mock.

If you need to test the scheduler or real HTTP fetches, prefer adding
`respx` mocks over hitting the network.
