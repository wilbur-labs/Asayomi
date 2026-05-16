"""Auth gate for /api/v1/system/* — require_admin_token dependency.

The /system/* routes drive Azure OpenAI calls, external HTTP fetches,
and outbound notifications. They must NOT be reachable anonymously.
"""
import pytest

from app.core.config import settings


@pytest.fixture
def admin_token(monkeypatch):
    """Set ADMIN_TOKEN on the live settings object for the duration of one test."""
    monkeypatch.setattr(settings, "admin_token", "test-secret")
    return "test-secret"


def test_returns_503_when_admin_token_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_token", None)
    r = client.post("/api/v1/system/collect")
    assert r.status_code == 503
    assert "ADMIN_TOKEN" in r.json()["detail"]


def test_returns_401_when_token_missing(client, admin_token):
    r = client.post("/api/v1/system/collect")
    assert r.status_code == 401


def test_returns_401_when_token_wrong(client, admin_token):
    r = client.post(
        "/api/v1/system/collect",
        headers={"X-Asayomi-Admin-Token": "wrong"},
    )
    assert r.status_code == 401


def test_all_system_endpoints_are_gated(client, monkeypatch):
    """Spot-check that the gate applies to every /system/* route, not just /collect."""
    monkeypatch.setattr(settings, "admin_token", "test-secret")
    paths = [
        "/api/v1/system/collect",
        "/api/v1/system/dedupe",
        "/api/v1/system/process",
        "/api/v1/system/briefing",
        "/api/v1/system/briefing/weekly",
        "/api/v1/system/briefing/monthly",
        "/api/v1/system/notify",
        "/api/v1/system/run-all",
    ]
    for path in paths:
        r = client.post(path)
        assert r.status_code == 401, f"{path} did not require auth"


def test_correct_token_passes_gate(client, admin_token, monkeypatch):
    """With the right token, the gate lets the call through. We mock the
    underlying service so the test doesn't perform real RSS fetches."""
    # The on-main system.py uses a lazy `from ..services.data_collector import collect_all`
    # inside the handler — so we have to patch the source module, not api.system.
    import app.services.data_collector as collector_mod
    monkeypatch.setattr(collector_mod, "collect_all", lambda fetch_fulltext=True: 7)

    r = client.post(
        "/api/v1/system/collect",
        headers={"X-Asayomi-Admin-Token": admin_token},
    )
    assert r.status_code == 200
    assert r.json() == {"message": "収集完了: 7 件"}
