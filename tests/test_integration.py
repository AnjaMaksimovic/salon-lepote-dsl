"""Integration checks for the app wiring and domain endpoints."""
from generated.test_api import api


def test_frontend_and_docs(api):
    client, _, _ = api
    response = client.get("/")
    assert response.status_code == 200
    assert "Administration" in response.text
    assert response.headers["cache-control"] == "no-cache, must-revalidate"
    for name in ("client", "package", "worker", "appointment", "service"):
        for kind in ("form", "list"):
            response = client.get(f"/app/{kind}_{name}.html")
            assert response.status_code == 200
            assert response.text.count("<!DOCTYPE html>") == 1
            assert "http://127.0.0.1:8000" not in response.text
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_partial_update_and_null_rejection(api):
    client, _, ids = api
    path = f"/worker/{ids['Worker']}"
    before = client.get(path).json()
    response = client.put(path, json={"name": "New name"})
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "New name"
    assert response.json()["service"] == before["service"]
    assert client.put(path, json={"name": None}).status_code == 422
    assert client.get(path).json()["name"] == "New name"


def test_invalid_references_and_referenced_delete(api):
    client, _, ids = api
    assert client.put(f"/appointment/{ids['Appointment']}", json={"client_id": 99999}).status_code == 400
    assert client.put(f"/worker/{ids['Worker']}", json={"service_ids": [99999]}).status_code == 400
    assert client.delete(f"/client/{ids['Client']}").status_code == 409
    assert client.get(f"/client/{ids['Client']}").status_code == 200
    assert client.put("/client/99999", json={"name": "Missing"}).status_code == 404
    assert client.delete("/client/99999").status_code == 404


def test_business_rules_reject_invalid_updates(api):
    client, _, ids = api
    path = f"/appointment/{ids['Appointment']}"
    assert client.put(path, json={"durationMinutes": 0}).status_code == 400
    assert client.get(path).json()["durationMinutes"] == 1
    worker = client.post("/worker/", json={"name": "Other", "surname": "Worker", "workingHoursFrom": "08:00:00", "workingHoursTo": "16:00:00"}).json()
    assert client.put(path, json={"worker_id": worker["id"]}).status_code == 400
    assert client.put(f"/package/{ids['Package']}", json={"price": 100}).status_code == 400


def test_revenue_and_availability(api):
    client, _, ids = api
    response = client.get("/reports/revenue", params={"date_from": "2026-09-10T00:00:00", "date_to": "2026-09-11T00:00:00"})
    assert response.status_code == 200, response.text
    assert response.json() == {"appointment_count": 1, "total_revenue": 1.0}
    query = {"worker_id": ids["Worker"], "service_ids": str(ids["Service"]), "date_time": "2026-09-10T10:00:00", "duration_minutes": 1}
    assert client.get("/appointments/suggestions", params=query).json()["available"] is False
    query["date_time"] = "2026-09-10T10:01:00"
    assert client.get("/appointments/suggestions", params=query).json()["available"] is True
    query["service_ids"] = "not-an-id"
    assert client.get("/appointments/suggestions", params=query).status_code == 422
    assert client.get("/reports/revenue", params={"date_from": "bad", "date_to": "bad"}).status_code == 422


def test_english_api_and_worker_form(api):
    client, _, _ = api
    spec = client.get("/openapi.json").json()
    for name in ("client", "worker", "service", "package", "appointment"):
        assert f"/{name}/" in spec["paths"]
    fields = spec["components"]["schemas"]["ClientCreate"]["properties"]
    assert set(fields) == {"name", "email", "phone"}
    assert spec["components"]["schemas"]["AppointmentStatus"]["enum"] == ["COMPLETED", "CANCELLED", "SCHEDULED"]
    form = client.get("/app/form_worker.html").text
    assert 'lang="en"' in form
    assert form.index('name="workingHoursFrom"') < form.index('name="workingHoursTo"')
    assert "Save" in form and "Back to list" in form
