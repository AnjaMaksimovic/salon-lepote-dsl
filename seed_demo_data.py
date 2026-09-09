"""Seeds salon.db with a realistic demo dataset for manual testing and the project defense.

Unlike generated/seed_data.py (placeholder data regenerated from the model), this script is
maintained manually and is safe to keep across `generator/generate.py` runs. By default it
drops and recreates all tables so re-running it always leaves a clean, known dataset behind.

Usage (from the project root, with the virtualenv active):
    python seed_demo_data.py
    python seed_demo_data.py --keep-existing   # add to existing data instead of resetting
"""
import argparse
from datetime import date, time, datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from generated.entities import Base
from generated import association_tables  # noqa: F401  (registers many-to-many tables)
from generated import repository as repo
from generated import schema


def seed(db: Session):
    ids = {}

    # --- Clients ---------------------------------------------------------
    clients = [
        ("jelena.markovic@example.com", "Jelena Markovic", "0601234567"),
        ("marina.djordjevic@example.com", "Marina Djordjevic", "0652345678"),
        ("ivana.simic@example.com", "Ivana Simic", "0633456789"),
        ("sofija.ilic@example.com", "Sofija Ilic", "0644567890"),
        ("tamara.kovacevic@example.com", "Tamara Kovacevic", "0615678901"),
    ]
    ids["clients"] = []
    for email, name, phone in clients:
        obj = repo.create_client(db, schema.ClientCreate(email=email, name=name, phone=phone))
        ids["clients"].append(obj.id)
        print(f"Created Client id={obj.id} ({name})")

    # --- Services ----------------------------------------------------------
    # (name, category, price, durationMinutes)
    services = [
        ("Haircut", "HAIRCUT", 1500.0, 30),
        ("Hair coloring", "HAIRCUT", 3500.0, 90),
        ("Leg waxing", "HAIR_REMOVAL", 2000.0, 45),
        ("Arm waxing", "HAIR_REMOVAL", 1200.0, 30),
        ("Lash lift", "LASH_BROW", 2500.0, 60),
        ("Eyebrow shaping", "LASH_BROW", 1000.0, 20),
        ("Manicure", "MANICURE_PEDICURE", 1800.0, 45),
        ("Pedicure", "MANICURE_PEDICURE", 2200.0, 60),
        ("Facial treatment", "FACIAL_CARE", 3000.0, 60),
    ]
    ids["services"] = []
    for name, category, price, duration in services:
        obj = repo.create_service(db, schema.ServiceCreate(
            name=name, category=category, price=price, durationMinutes=duration,
        ))
        ids["services"].append(obj.id)
        print(f"Created Service id={obj.id} ({name})")
    S = dict(zip((s[0] for s in services), ids["services"]))

    # --- Workers (each qualified for a realistic subset of services) -----
    workers = [
        ("Ana", "Jovanovic", time(9, 0), time(17, 0), ["Haircut", "Hair coloring"]),
        ("Milica", "Petrovic", time(10, 0), time(18, 0), ["Leg waxing", "Arm waxing", "Lash lift", "Eyebrow shaping"]),
        ("Jovana", "Nikolic", time(9, 0), time(15, 0), ["Manicure", "Pedicure"]),
        ("Marija", "Stankovic", time(12, 0), time(20, 0), ["Facial treatment", "Eyebrow shaping"]),
    ]
    ids["workers"] = []
    for name, surname, work_from, work_to, service_names in workers:
        obj = repo.create_worker(db, schema.WorkerCreate(
            name=name, surname=surname,
            workingHoursFrom=work_from, workingHoursTo=work_to,
            service_ids=[S[n] for n in service_names],
        ))
        ids["workers"].append(obj.id)
        print(f"Created Worker id={obj.id} ({name} {surname})")
    W = dict(zip((w[0] for w in workers), ids["workers"]))

    # --- Packages (price kept below the combined service price) ----------
    packages = [
        ("Nail care package", 3500.0, ["Manicure", "Pedicure"]),          # 1800+2200=4000
        ("Face & brows package", 3600.0, ["Facial treatment", "Eyebrow shaping"]),  # 3000+1000=4000
    ]
    ids["packages"] = []
    for name, price, service_names in packages:
        obj = repo.create_package(db, schema.PackageCreate(
            name=name, price=price, service_ids=[S[n] for n in service_names],
        ))
        ids["packages"].append(obj.id)
        print(f"Created Package id={obj.id} ({name})")

    # --- Appointments ------------------------------------------------------
    # Reference "today" for the demo timeline: 2026-09-09.
    # Past dates -> COMPLETED (feeds /reports/revenue), future dates -> SCHEDULED,
    # one CANCELLED appointment to show it is excluded from revenue/overlap checks.
    C = ids["clients"]
    appointments = [
        # client, worker, datetime,               duration, status,      services
        (C[0], W["Ana"],     datetime(2026, 9, 1, 10, 0), 30,  "COMPLETED", ["Haircut"]),
        (C[1], W["Ana"],     datetime(2026, 9, 2, 11, 0), 90,  "COMPLETED", ["Hair coloring"]),
        (C[2], W["Milica"],  datetime(2026, 9, 3, 10, 0), 75,  "COMPLETED", ["Leg waxing", "Arm waxing"]),
        (C[3], W["Jovana"],  datetime(2026, 9, 4, 9, 0),  105, "COMPLETED", ["Manicure", "Pedicure"]),
        (C[4], W["Marija"],  datetime(2026, 9, 5, 12, 0), 60,  "COMPLETED", ["Facial treatment"]),
        (C[0], W["Milica"],  datetime(2026, 9, 8, 10, 0), 60,  "CANCELLED", ["Lash lift"]),
        (C[1], W["Ana"],     datetime(2026, 9, 12, 10, 0), 30, "SCHEDULED", ["Haircut"]),
        (C[2], W["Jovana"],  datetime(2026, 9, 15, 9, 0), 45,  "SCHEDULED", ["Manicure"]),
        (C[3], W["Marija"],  datetime(2026, 9, 20, 12, 0), 20, "SCHEDULED", ["Eyebrow shaping"]),
    ]
    ids["appointments"] = []
    for client_id, worker_id, dt, duration, status, service_names in appointments:
        obj = repo.create_appointment(db, schema.AppointmentCreate(
            dateTime=dt, status=status, durationMinutes=duration,
            client_id=client_id, worker_id=worker_id,
            service_ids=[S[n] for n in service_names],
        ))
        ids["appointments"].append(obj.id)
        print(f"Created Appointment id={obj.id} ({status}, {dt.isoformat()})")

    return ids


def main():
    parser = argparse.ArgumentParser(description="Seed a realistic demo dataset into salon.db")
    parser.add_argument("--database-url", default="sqlite:///./salon.db")
    parser.add_argument("--keep-existing", action="store_true",
                        help="Do not drop existing tables first; add to whatever is already there.")
    args = parser.parse_args()

    engine = create_engine(args.database_url)
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    try:
        if not args.keep_existing:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            seed(db)
        print("Demo data inserted successfully.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
