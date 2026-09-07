"""API tests using an isolated in-memory database.

Run: python -m pytest generated/test_api.py -v
API tests require the application and database modules from commit 6.
"""
import importlib
import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from generated.entities import Base
from generated import association_tables
from generated.seed_data import seed

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def api(tmp_path, monkeypatch):
    if not (ROOT / "main.py").exists() or not (ROOT / "generated/database.py").exists():
        pytest.skip("API integration pending: main.py and generated/database.py are required (commit 6)")
    # Confine relative database paths and application startup writes to a temporary folder.
    monkeypatch.syspath_prepend(str(ROOT))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "generated/frontend").mkdir(parents=True)
    from fastapi.testclient import TestClient
    app = importlib.import_module("main").app
    get_db = importlib.import_module("generated.database").get_db
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    previous = dict(app.dependency_overrides)
    try:
        with Session(engine) as db:
            ids = seed(db)
        def override_get_db():
            with Session(engine) as db:
                yield db
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as client:
            yield client, engine, ids
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def test_klijent_crud(api):
    client, engine, ids = api
    payload = json.loads('{"email": "primer", "ime": "primer", "telefon": "primer"}')
    response = client.post("/klijent/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/klijent/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["email"] == payload["email"]
    assert response.json()["ime"] == payload["ime"]
    assert response.json()["telefon"] == payload["telefon"]
    response = client.get("/klijent/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["email"] = "updated"
    updated["ime"] = "updated"
    updated["telefon"] = "updated"
    response = client.put(f"/klijent/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/klijent/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["email"] == "updated"
    assert response.json()["ime"] == "updated"
    assert response.json()["telefon"] == "updated"
    response = client.delete(f"/klijent/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/klijent/{created_id}").status_code == 404


def test_klijent_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/klijent/", json={})
    assert response.status_code == 422, response.text


def test_paket_crud(api):
    client, engine, ids = api
    payload = json.loads('{"cena": 1.0, "naziv": "primer", "usluga_ids": [1]}')
    payload["usluga_ids"] = []
    response = client.post("/paket/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/paket/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["cena"] == payload["cena"]
    assert response.json()["naziv"] == payload["naziv"]
    response = client.get("/paket/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["naziv"] = "updated"
    response = client.put(f"/paket/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/paket/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["naziv"] == "updated"
    response = client.delete(f"/paket/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/paket/{created_id}").status_code == 404


def test_paket_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/paket/", json={})
    assert response.status_code == 422, response.text


def test_paket_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"cena": 1.0, "naziv": "primer", "usluga_ids": [1]}')
    payload["usluga_ids"] = [ids["Usluga"]]
    response = client.put(f"/paket/{ids['Paket']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_paket
        linked_ids = db.scalars(select(table.c.usluga_id).where(
            table.c.paket_id == ids["Paket"])).all()
        assert linked_ids == [ids["Usluga"]]
    # Removing links must also be persisted.
    payload["usluga_ids"] = []
    response = client.put(f"/paket/{ids['Paket']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_paket
        assert db.scalars(select(table.c.usluga_id).where(
            table.c.paket_id == ids["Paket"])).all() == []

def test_radnik_crud(api):
    client, engine, ids = api
    payload = json.loads('{"ime": "primer", "prezime": "primer", "radnoVremeDo": "10:00:00", "radnoVremeOd": "10:00:00", "usluga_ids": [1]}')
    payload["usluga_ids"] = []
    response = client.post("/radnik/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/radnik/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["ime"] == payload["ime"]
    assert response.json()["prezime"] == payload["prezime"]
    assert response.json()["radnoVremeDo"] == payload["radnoVremeDo"]
    assert response.json()["radnoVremeOd"] == payload["radnoVremeOd"]
    response = client.get("/radnik/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["ime"] = "updated"
    updated["prezime"] = "updated"
    response = client.put(f"/radnik/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/radnik/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["ime"] == "updated"
    assert response.json()["prezime"] == "updated"
    response = client.delete(f"/radnik/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/radnik/{created_id}").status_code == 404


def test_radnik_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/radnik/", json={})
    assert response.status_code == 422, response.text


def test_radnik_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"ime": "primer", "prezime": "primer", "radnoVremeDo": "10:00:00", "radnoVremeOd": "10:00:00", "usluga_ids": [1]}')
    payload["usluga_ids"] = [ids["Usluga"]]
    response = client.put(f"/radnik/{ids['Radnik']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_radnik
        linked_ids = db.scalars(select(table.c.usluga_id).where(
            table.c.radnik_id == ids["Radnik"])).all()
        assert linked_ids == [ids["Usluga"]]
    # Removing links must also be persisted.
    payload["usluga_ids"] = []
    response = client.put(f"/radnik/{ids['Radnik']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_radnik
        assert db.scalars(select(table.c.usluga_id).where(
            table.c.radnik_id == ids["Radnik"])).all() == []

def test_usluga_crud(api):
    client, engine, ids = api
    payload = json.loads('{"cena": 1.0, "kategorija": "DEPILACIJA", "naziv": "primer", "trajanjeMin": 1, "paket_ids": [1], "radnik_ids": [1], "termin_ids": [1]}')
    payload["paket_ids"] = []
    payload["radnik_ids"] = []
    payload["termin_ids"] = []
    response = client.post("/usluga/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/usluga/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["cena"] == payload["cena"]
    assert response.json()["kategorija"] == payload["kategorija"]
    assert response.json()["naziv"] == payload["naziv"]
    assert response.json()["trajanjeMin"] == payload["trajanjeMin"]
    response = client.get("/usluga/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["naziv"] = "updated"
    response = client.put(f"/usluga/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/usluga/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["naziv"] == "updated"
    response = client.delete(f"/usluga/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/usluga/{created_id}").status_code == 404


def test_usluga_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/usluga/", json={})
    assert response.status_code == 422, response.text


def test_usluga_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"cena": 1.0, "kategorija": "DEPILACIJA", "naziv": "primer", "trajanjeMin": 1, "paket_ids": [1], "radnik_ids": [1], "termin_ids": [1]}')
    payload["paket_ids"] = [ids["Paket"]]
    payload["radnik_ids"] = [ids["Radnik"]]
    payload["termin_ids"] = [ids["Termin"]]
    response = client.put(f"/usluga/{ids['Usluga']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_paket
        linked_ids = db.scalars(select(table.c.paket_id).where(
            table.c.usluga_id == ids["Usluga"])).all()
        assert linked_ids == [ids["Paket"]]
        table = association_tables.usluga_radnik
        linked_ids = db.scalars(select(table.c.radnik_id).where(
            table.c.usluga_id == ids["Usluga"])).all()
        assert linked_ids == [ids["Radnik"]]
        table = association_tables.usluga_termin
        linked_ids = db.scalars(select(table.c.termin_id).where(
            table.c.usluga_id == ids["Usluga"])).all()
        assert linked_ids == [ids["Termin"]]
    # Removing links must also be persisted.
    payload["paket_ids"] = []
    payload["radnik_ids"] = []
    payload["termin_ids"] = []
    response = client.put(f"/usluga/{ids['Usluga']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_paket
        assert db.scalars(select(table.c.paket_id).where(
            table.c.usluga_id == ids["Usluga"])).all() == []
        table = association_tables.usluga_radnik
        assert db.scalars(select(table.c.radnik_id).where(
            table.c.usluga_id == ids["Usluga"])).all() == []
        table = association_tables.usluga_termin
        assert db.scalars(select(table.c.termin_id).where(
            table.c.usluga_id == ids["Usluga"])).all() == []

def test_termin_crud(api):
    client, engine, ids = api
    payload = json.loads('{"datumVreme": "2026-09-10T10:00:00", "status": "ODRZAN", "trajanjeMin": 1, "klijent_id": 1, "radnik_id": 1, "usluga_ids": [1]}')
    payload["klijent_id"] = ids["Klijent"]
    payload["radnik_id"] = ids["Radnik"]
    payload["usluga_ids"] = []
    response = client.post("/termin/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/termin/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["datumVreme"] == payload["datumVreme"]
    assert response.json()["status"] == payload["status"]
    assert response.json()["trajanjeMin"] == payload["trajanjeMin"]
    response = client.get("/termin/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    response = client.put(f"/termin/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/termin/{created_id}")
    assert response.status_code == 200, response.text
    response = client.delete(f"/termin/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/termin/{created_id}").status_code == 404


def test_termin_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/termin/", json={})
    assert response.status_code == 422, response.text


def test_termin_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"datumVreme": "2026-09-10T10:00:00", "status": "ODRZAN", "trajanjeMin": 1, "klijent_id": 1, "radnik_id": 1, "usluga_ids": [1]}')
    payload["klijent_id"] = ids["Klijent"]
    payload["radnik_id"] = ids["Radnik"]
    payload["usluga_ids"] = [ids["Usluga"]]
    response = client.put(f"/termin/{ids['Termin']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_termin
        linked_ids = db.scalars(select(table.c.usluga_id).where(
            table.c.termin_id == ids["Termin"])).all()
        assert linked_ids == [ids["Usluga"]]
    # Removing links must also be persisted.
    payload["usluga_ids"] = []
    response = client.put(f"/termin/{ids['Termin']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.usluga_termin
        assert db.scalars(select(table.c.usluga_id).where(
            table.c.termin_id == ids["Termin"])).all() == []
