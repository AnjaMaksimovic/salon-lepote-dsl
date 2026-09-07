# Beauty Salon DSL

A model-driven beauty salon application. The project uses a B-UML domain model to generate database entities, CRUD API code, validation functions, frontend pages and API tests.

The goal is to define the domain once and reuse it across the application instead of writing each entity, endpoint and form separately. The model describes clients, workers, services, packages and appointments, including their relationships and OCL constraints.

## How it works

1. `model/salon_model.py` defines the domain with BESSER/B-UML Python objects.
2. `generator/generate.py` reads classes, attributes, enumerations, associations and constraints from that model.
3. Jinja2 templates turn this information into files under `generated/`.
4. `main.py` connects the generated API, SQLite database and frontend in one FastAPI application.

The source model in `model/salon_model.py` keeps its original Serbian identifiers. `generator/english.py` maps them to English class names, fields, enum values, database tables, API routes and frontend labels without modifying the model. The generator translates supported OCL expression patterns into Python validation functions; it is not a complete OCL interpreter.

## Technologies

- Python and BESSER/B-UML: domain model and generator.
- Jinja2: code and page templates.
- SQLAlchemy and SQLite: database persistence and relationships.
- Pydantic and FastAPI: request validation and REST API.
- HTML, CSS and JavaScript: generated frontend.
- pytest and FastAPI TestClient: automated API and integration tests.

## Project structure

| Path | Purpose |
|---|---|
| `model/salon_model.py` | Domain model, relationships and OCL constraints |
| `generator/english.py` | English naming map for the unchanged source model |
| `generator/generate.py` | Context preparation and template rendering |
| `generator/templates/` | Templates for Python code, pages and tests |
| `generator/business_rules.py` | Existing manual rule checks copied into generated output |
| `generated/` | Generated entities, schemas, repository, API, frontend, seed script and tests |
| `main.py` | Application startup, API registration and frontend serving |
| `business_rules.py` | Manual revenue and appointment-availability logic |
| `tests/test_integration.py` | Application integration and business-endpoint checks |
| `requirements.txt` | Dependency versions used for local verification |

Keep `model/salon_model.py` unchanged when translating the app; adjust `generator/english.py` or the templates, then regenerate. Editing only a generated file is temporary: the next generation overwrites it. `main.py`, the root `business_rules.py` and integration tests are maintained manually.

## Setup on Windows

Run the commands in PowerShell from the `salon-lepote-dsl` project root. Python 3.12 is a suitable starting point; dependency installation must complete successfully before continuing.

Create the virtual environment once if `.venv` does not already exist:

```powershell
python -m venv .venv
```

Install dependencies and generate the application:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe generator/generate.py
```

Start the API and frontend together:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open:

- [Frontend](http://127.0.0.1:8000/app/index.html)
- [Interactive API documentation](http://127.0.0.1:8000/docs)

Keep the terminal running. Press **Ctrl+C** to stop the server. Database tables are created on application startup. Creating, editing and deleting records through the frontend uses the API and persists changes in `salon.db`.

Do not use `python -m http.server` for the full application: it only serves files and cannot process API requests or save records.

If port 8000 is occupied, stop the previous server or use:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

Then open [the frontend on port 8001](http://127.0.0.1:8001/app/index.html). Generated pages use relative API URLs, so they work on either port.

## Entering data through the frontend

Use this order when starting with an empty database:

1. **Client:** add a client with a name, email and phone number.
2. **Service:** add a service, for example a haircut costing **1000** and lasting **30 minutes**, with category **HAIRCUT**. Leave worker, package and appointment links unselected for now.
3. **Worker:** enter a worker's name, surname and working hours, with the start time before the end time. Select the service that this worker performs.
4. **Package:** add a package, select its services and enter a price below their combined price. For the service above, **900** is valid and **1000** is not.
5. **Appointment:** select a client, worker, date/time, status **SCHEDULED** and services. The worker must perform the selected services, and the appointment duration must cover their total duration.

A package is optional when creating an appointment. Use the list page to edit or delete a record. Deleting a client or worker that is still referenced by an appointment is rejected to preserve those relationships.

## Sample data

Instead of entering records manually, open a second terminal in the project root and run:

```powershell
.\.venv\Scripts\python.exe -m generated.seed_data
```

The seed script creates one sample record per class in foreign-key dependency order, then connects many-to-many relationships in a second pass. It uses the IDs actually assigned by the database. Each run adds another dataset; it does not clear existing records.

Generic seed data is not guaranteed to satisfy all domain rules. In particular, the sample package may need a lower price before it can be saved through the API. The seed script inserts through the repository, while API writes apply the generated business validation.

To verify the seed script without changing the development database:

```powershell
.\.venv\Scripts\python.exe -m generated.seed_data --database-url sqlite:///:memory:
```

The application uses `salon.db` in the project root by default. Set `DATABASE_URL` before starting the server to choose a different database. The seed script takes its database URL separately through `--database-url`; run it from the project root to target the default `salon.db`.

## Tests

Generate the latest files, then run both test suites:

```powershell
.\.venv\Scripts\python.exe generator/generate.py
.\.venv\Scripts\python.exe -m pytest generated/test_api.py tests -v
```

The current suite contains **20 tests**:

- 14 generated tests covering CRUD operations, missing required fields and many-to-many links.
- 6 integration tests covering frontend/API wiring, partial updates, invalid references, business rules, revenue and worker availability.

Tests use isolated in-memory databases and do not modify `salon.db`. Expected result: **20 passed**, with no skipped tests. Compatibility deprecation warnings from dependencies may still appear.

For a manual check, create a client, confirm it appears in the list, edit its name, refresh the page and then delete it. The create/edit/list/delete flow was also checked in a headless browser.

## API routes

CRUD endpoints use `/client/`, `/worker/`, `/service/`, `/package/` and `/appointment/`. Their request and response field names and enum values are also English; see `/docs` for the schemas. For example, a client uses `name`, `email` and `phone`, and an appointment uses `dateTime`, `durationMinutes`, `client_id`, `worker_id` and `service_ids`.

The English schema replaces the old Serbian database schema. This update resets the local development database; old data is not migrated. The SQLite filename remains `salon.db`.

## Additional endpoints

| Endpoint | Parameters | Purpose |
|---|---|---|
| `/reports/revenue` | `date_from`, `date_to` | Count completed appointments and sum their service prices within a datetime range |
| `/appointments/suggestions` | `worker_id`, `service_ids`, `date_time`, `duration_minutes` | Check a worker's availability or suggest another qualified worker |

Use `/docs` to try these endpoints. Datetimes use local ISO format, for example `2026-09-10T10:00:00`. Service IDs are comma-separated, for example `1,2`.

## Current limits

- Availability checks worker qualifications and overlapping non-cancelled appointments, but does not currently enforce working hours. The suggestion endpoint does not reserve an appointment or automatically prevent overlaps in CRUD requests.
- Revenue uses current service prices for completed appointments, not historical invoices or package discounts.
- Only the OCL patterns implemented by the generator are translated. Other expressions require additional implementation.
- The application is a local educational prototype without authentication or access roles.
