"""API tests using an isolated in-memory database.

Run: python -m pytest generated/test_api.py -v
Each test uses fresh sample records and an isolated database.
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
        pytest.fail("Run the generator and provide main.py before running API tests")
    # Confine relative database paths and application startup writes to a temporary folder.
    monkeypatch.syspath_prepend(str(ROOT))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
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


def test_client_crud(api):
    client, engine, ids = api
    payload = json.loads('{"email": "sample", "name": "sample", "phone": "sample"}')
    response = client.post("/client/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/client/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["email"] == payload["email"]
    assert response.json()["name"] == payload["name"]
    assert response.json()["phone"] == payload["phone"]
    response = client.get("/client/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["email"] = "updated"
    updated["name"] = "updated"
    updated["phone"] = "updated"
    response = client.put(f"/client/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/client/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["email"] == "updated"
    assert response.json()["name"] == "updated"
    assert response.json()["phone"] == "updated"
    response = client.delete(f"/client/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/client/{created_id}").status_code == 404


def test_client_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/client/", json={})
    assert response.status_code == 422, response.text


def test_package_crud(api):
    client, engine, ids = api
    payload = json.loads('{"price": 1.0, "name": "sample", "service_ids": [1]}')
    payload["service_ids"] = []
    # The model requires the package price to be below its services' total.
    payload["price"] = 0.5
    payload["service_ids"] = [ids["Service"]]
    response = client.post("/package/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/package/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["price"] == payload["price"]
    assert response.json()["name"] == payload["name"]
    response = client.get("/package/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["name"] = "updated"
    response = client.put(f"/package/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/package/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "updated"
    response = client.delete(f"/package/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/package/{created_id}").status_code == 404


def test_package_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/package/", json={})
    assert response.status_code == 422, response.text


def test_package_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"price": 1.0, "name": "sample", "service_ids": [1]}')
    payload["service_ids"] = [ids["Service"]]
    payload["price"] = 0.5
    response = client.put(f"/package/{ids['Package']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_package
        linked_ids = db.scalars(select(table.c.service_id).where(
            table.c.package_id == ids["Package"])).all()
        assert linked_ids == [ids["Service"]]
    # Removing links must also be persisted.
    payload["service_ids"] = []
    response = client.put(f"/package/{ids['Package']}", json=payload)
    # Empty services would violate the package price rule; keep existing links.
    assert response.status_code == 400, response.text
    with Session(engine) as db:
        table = association_tables.service_package
        assert db.scalars(select(table.c.service_id).where(
            table.c.package_id == ids["Package"])).all() == [ids["Service"]]

def test_service_crud(api):
    client, engine, ids = api
    payload = json.loads('{"price": 1.0, "category": "HAIR_REMOVAL", "name": "sample", "durationMinutes": 1, "package_ids": [1], "worker_ids": [1], "appointment_ids": [1]}')
    payload["package_ids"] = []
    payload["worker_ids"] = []
    payload["appointment_ids"] = []
    response = client.post("/service/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/service/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["price"] == payload["price"]
    assert response.json()["category"] == payload["category"]
    assert response.json()["name"] == payload["name"]
    assert response.json()["durationMinutes"] == payload["durationMinutes"]
    response = client.get("/service/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["name"] = "updated"
    response = client.put(f"/service/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/service/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "updated"
    response = client.delete(f"/service/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/service/{created_id}").status_code == 404


def test_service_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/service/", json={})
    assert response.status_code == 422, response.text


def test_service_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"price": 1.0, "category": "HAIR_REMOVAL", "name": "sample", "durationMinutes": 1, "package_ids": [1], "worker_ids": [1], "appointment_ids": [1]}')
    payload["package_ids"] = [ids["Package"]]
    payload["worker_ids"] = [ids["Worker"]]
    payload["appointment_ids"] = [ids["Appointment"]]
    response = client.put(f"/service/{ids['Service']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_package
        linked_ids = db.scalars(select(table.c.package_id).where(
            table.c.service_id == ids["Service"])).all()
        assert linked_ids == [ids["Package"]]
        table = association_tables.service_worker
        linked_ids = db.scalars(select(table.c.worker_id).where(
            table.c.service_id == ids["Service"])).all()
        assert linked_ids == [ids["Worker"]]
        table = association_tables.service_appointment
        linked_ids = db.scalars(select(table.c.appointment_id).where(
            table.c.service_id == ids["Service"])).all()
        assert linked_ids == [ids["Appointment"]]
    # Removing links must also be persisted.
    payload["package_ids"] = []
    payload["worker_ids"] = []
    payload["appointment_ids"] = []
    response = client.put(f"/service/{ids['Service']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_package
        assert db.scalars(select(table.c.package_id).where(
            table.c.service_id == ids["Service"])).all() == []
        table = association_tables.service_worker
        assert db.scalars(select(table.c.worker_id).where(
            table.c.service_id == ids["Service"])).all() == []
        table = association_tables.service_appointment
        assert db.scalars(select(table.c.appointment_id).where(
            table.c.service_id == ids["Service"])).all() == []

def test_worker_crud(api):
    client, engine, ids = api
    payload = json.loads('{"name": "sample", "surname": "sample", "workingHoursTo": "10:00:00", "workingHoursFrom": "10:00:00", "service_ids": [1]}')
    payload["service_ids"] = []
    response = client.post("/worker/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/worker/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["name"] == payload["name"]
    assert response.json()["surname"] == payload["surname"]
    assert response.json()["workingHoursTo"] == payload["workingHoursTo"]
    assert response.json()["workingHoursFrom"] == payload["workingHoursFrom"]
    response = client.get("/worker/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    updated["name"] = "updated"
    updated["surname"] = "updated"
    response = client.put(f"/worker/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/worker/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "updated"
    assert response.json()["surname"] == "updated"
    response = client.delete(f"/worker/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/worker/{created_id}").status_code == 404


def test_worker_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/worker/", json={})
    assert response.status_code == 422, response.text


def test_worker_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"name": "sample", "surname": "sample", "workingHoursTo": "10:00:00", "workingHoursFrom": "10:00:00", "service_ids": [1]}')
    payload["service_ids"] = [ids["Service"]]
    response = client.put(f"/worker/{ids['Worker']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_worker
        linked_ids = db.scalars(select(table.c.service_id).where(
            table.c.worker_id == ids["Worker"])).all()
        assert linked_ids == [ids["Service"]]
    # Removing links must also be persisted.
    payload["service_ids"] = []
    response = client.put(f"/worker/{ids['Worker']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_worker
        assert db.scalars(select(table.c.service_id).where(
            table.c.worker_id == ids["Worker"])).all() == []

def test_appointment_crud(api):
    client, engine, ids = api
    payload = json.loads('{"dateTime": "2026-09-10T10:00:00", "status": "COMPLETED", "durationMinutes": 1, "client_id": 1, "worker_id": 1, "service_ids": [1]}')
    payload["client_id"] = ids["Client"]
    payload["worker_id"] = ids["Worker"]
    payload["service_ids"] = []
    response = client.post("/appointment/", json=payload)
    assert response.status_code == 200, response.text
    created_id = response.json()["id"]
    response = client.get(f"/appointment/{created_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == created_id
    assert response.json()["dateTime"] == payload["dateTime"]
    assert response.json()["status"] == payload["status"]
    assert response.json()["durationMinutes"] == payload["durationMinutes"]
    response = client.get("/appointment/")
    assert response.status_code == 200, response.text
    assert any(item["id"] == created_id for item in response.json())
    updated = dict(payload)
    response = client.put(f"/appointment/{created_id}", json=updated)
    assert response.status_code == 200, response.text
    response = client.get(f"/appointment/{created_id}")
    assert response.status_code == 200, response.text
    response = client.delete(f"/appointment/{created_id}")
    assert response.status_code == 200, response.text
    assert client.get(f"/appointment/{created_id}").status_code == 404


def test_appointment_rejects_missing_fields(api):
    client, _, _ = api
    response = client.post("/appointment/", json={})
    assert response.status_code == 422, response.text


def test_appointment_many_to_many_links(api):
    client, engine, ids = api
    payload = json.loads('{"dateTime": "2026-09-10T10:00:00", "status": "COMPLETED", "durationMinutes": 1, "client_id": 1, "worker_id": 1, "service_ids": [1]}')
    payload["client_id"] = ids["Client"]
    payload["worker_id"] = ids["Worker"]
    payload["service_ids"] = [ids["Service"]]
    response = client.put(f"/appointment/{ids['Appointment']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_appointment
        linked_ids = db.scalars(select(table.c.service_id).where(
            table.c.appointment_id == ids["Appointment"])).all()
        assert linked_ids == [ids["Service"]]
    # Removing links must also be persisted.
    payload["service_ids"] = []
    response = client.put(f"/appointment/{ids['Appointment']}", json=payload)
    assert response.status_code == 200, response.text
    with Session(engine) as db:
        table = association_tables.service_appointment
        assert db.scalars(select(table.c.service_id).where(
            table.c.appointment_id == ids["Appointment"])).all() == []
