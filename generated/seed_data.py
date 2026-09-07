"""Populates the database with sample data and links many-to-many relationships."""
import argparse
import json
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from generated.entities import Base
from generated import association_tables  # Registers many-to-many tables.
from generated import repository as repo
from generated import schema


def seed(db):
    created_ids = {}
    payloads = {}
    print("--- Pass 1: creating records ---")
    data = json.loads('{"email": "sample", "name": "sample", "phone": "sample"}')
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Client"] = data
    obj = repo.create_client(db, schema.ClientCreate(**data))
    created_ids["Client"] = obj.id
    print("Created Client id=", obj.id)
    data = json.loads('{"price": 1.0, "name": "sample", "service_ids": [1]}')
    data["service_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Package"] = data
    obj = repo.create_package(db, schema.PackageCreate(**data))
    created_ids["Package"] = obj.id
    print("Created Package id=", obj.id)
    data = json.loads('{"price": 1.0, "category": "HAIR_REMOVAL", "name": "sample", "durationMinutes": 1, "package_ids": [1], "worker_ids": [1], "appointment_ids": [1]}')
    data["package_ids"] = []
    data["worker_ids"] = []
    data["appointment_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Service"] = data
    obj = repo.create_service(db, schema.ServiceCreate(**data))
    created_ids["Service"] = obj.id
    print("Created Service id=", obj.id)
    data = json.loads('{"name": "sample", "surname": "sample", "workingHoursTo": "10:00:00", "workingHoursFrom": "10:00:00", "service_ids": [1]}')
    data["service_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Worker"] = data
    obj = repo.create_worker(db, schema.WorkerCreate(**data))
    created_ids["Worker"] = obj.id
    print("Created Worker id=", obj.id)
    data = json.loads('{"dateTime": "2026-09-10T10:00:00", "status": "COMPLETED", "durationMinutes": 1, "client_id": 1, "worker_id": 1, "service_ids": [1]}')
    data["client_id"] = created_ids["Client"]
    data["worker_id"] = created_ids["Worker"]
    data["service_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Appointment"] = data
    obj = repo.create_appointment(db, schema.AppointmentCreate(**data))
    created_ids["Appointment"] = obj.id
    print("Created Appointment id=", obj.id)

    print("--- Pass 2: linking many-to-many relationships ---")
    data = dict(payloads["Package"])
    data["service_ids"] = [created_ids["Service"]]
    repo.update_package(db, created_ids["Package"], schema.PackageCreate(**data))
    print("Linked many-to-many relationships: Package")
    data = dict(payloads["Service"])
    data["package_ids"] = [created_ids["Package"]]
    data["worker_ids"] = [created_ids["Worker"]]
    data["appointment_ids"] = [created_ids["Appointment"]]
    repo.update_service(db, created_ids["Service"], schema.ServiceCreate(**data))
    print("Linked many-to-many relationships: Service")
    data = dict(payloads["Worker"])
    data["service_ids"] = [created_ids["Service"]]
    repo.update_worker(db, created_ids["Worker"], schema.WorkerCreate(**data))
    print("Linked many-to-many relationships: Worker")
    data = dict(payloads["Appointment"])
    data["service_ids"] = [created_ids["Service"]]
    repo.update_appointment(db, created_ids["Appointment"], schema.AppointmentCreate(**data))
    print("Linked many-to-many relationships: Appointment")
    return created_ids


def main():
    parser = argparse.ArgumentParser(description="Insert sample records and many-to-many relationships")
    parser.add_argument("--database-url", default="sqlite:///./salon.db")
    args = parser.parse_args()
    engine = create_engine(args.database_url)
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            seed(db)
        print("Seed data inserted successfully.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()