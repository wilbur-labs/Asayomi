"""Source 永続化 — toggle が再起動を跨いでも残る。

このテストが守るのは『Sources ページで無効化したソースが、コンテナ
再起動後にまた有効に戻ってしまう』というユーザー体験のバグ。
"""
from app.models.source import Source
from app.services.sources import DEFAULT_SOURCES, seed_sources_if_empty


def test_seed_populates_empty_table(db_session):
    assert db_session.query(Source).count() == 0
    added = seed_sources_if_empty(db_session)
    assert added == len(DEFAULT_SOURCES)
    assert db_session.query(Source).count() == len(DEFAULT_SOURCES)


def test_seed_is_idempotent(db_session):
    seed_sources_if_empty(db_session)
    # Second call must NOT touch the table — user toggles would otherwise
    # be overwritten on every container restart.
    added = seed_sources_if_empty(db_session)
    assert added == 0
    assert db_session.query(Source).count() == len(DEFAULT_SOURCES)


def test_seed_skips_when_user_changed_data(db_session):
    """ユーザーが全ソースを削除して 1 件だけ残しても、seed は介入しない。"""
    db_session.add(Source(name="My Only", url="https://x", category="総合", language="ja", enabled=True))
    db_session.commit()
    added = seed_sources_if_empty(db_session)
    assert added == 0
    assert db_session.query(Source).count() == 1


def test_list_sources_returns_seeded_data(client, db_session):
    seed_sources_if_empty(db_session)
    r = client.get("/api/v1/sources")
    assert r.status_code == 200
    body = r.json()
    names = [s["name"] for s in body["sources"]]
    assert "NHK News Web" in names
    assert "The Japan Times" in names


def test_toggle_persists_in_db(client, db_session):
    seed_sources_if_empty(db_session)
    # Disable a source via the API
    r = client.post(
        "/api/v1/sources/NHK News Web/toggle",
        json={"enabled": False},
    )
    assert r.status_code == 200

    # Simulate "process restart" — open a fresh session, the change must persist.
    db_session.expire_all()
    src = db_session.query(Source).filter(Source.name == "NHK News Web").one()
    assert src.enabled is False


def test_toggle_404_for_unknown_source(client, db_session):
    seed_sources_if_empty(db_session)
    r = client.post(
        "/api/v1/sources/no-such-source/toggle",
        json={"enabled": False},
    )
    assert r.status_code == 404


def test_disabled_source_excluded_from_collect_all(db_session, monkeypatch):
    """collect_all は無効化されたソースを飛ばす。RSS フェッチが走らないことを確認。"""
    from app.services import data_collector

    seed_sources_if_empty(db_session)
    # Disable everything except NHK
    for s in db_session.query(Source).all():
        s.enabled = s.name == "NHK News Web"
    db_session.commit()

    visited = []
    def fake_collect_from_source(db, source, fetch_fulltext=False):
        visited.append(source.name)
        return 0
    monkeypatch.setattr(data_collector, "collect_from_source", fake_collect_from_source)

    data_collector.collect_all(fetch_fulltext=False)
    assert visited == ["NHK News Web"]
