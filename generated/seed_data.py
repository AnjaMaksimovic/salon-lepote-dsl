"""AUTO-GENERISANO. Kreira primer svake klase, zatim povezuje N:N veze.

Pokretanje: python -m generated.seed_data
Izolovana provera: python -m generated.seed_data --database-url sqlite:///:memory:
Podaci su demonstracioni; nisu garantovano validni za sva OCL pravila.
Svako pokretanje dodaje novi skup podataka.
"""
import argparse
import json
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from generated.entities import Base
from generated import association_tables  # Registers N:N tables.
from generated import repository as repo
from generated import schema


def seed(db):
    created_ids = {}
    payloads = {}
    print("--- Prolaz 1: kreiranje zapisa ---")
    data = json.loads('{"email": "primer", "ime": "primer", "telefon": "primer"}')
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Klijent"] = data
    obj = repo.create_klijent(db, schema.KlijentCreate(**data))
    created_ids["Klijent"] = obj.id
    print("Kreiran(a) Klijent id=", obj.id)
    data = json.loads('{"cena": 1.0, "naziv": "primer", "usluga_ids": [1]}')
    data["usluga_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Paket"] = data
    obj = repo.create_paket(db, schema.PaketCreate(**data))
    created_ids["Paket"] = obj.id
    print("Kreiran(a) Paket id=", obj.id)
    data = json.loads('{"ime": "primer", "prezime": "primer", "radnoVremeDo": "10:00:00", "radnoVremeOd": "10:00:00", "usluga_ids": [1]}')
    data["usluga_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Radnik"] = data
    obj = repo.create_radnik(db, schema.RadnikCreate(**data))
    created_ids["Radnik"] = obj.id
    print("Kreiran(a) Radnik id=", obj.id)
    data = json.loads('{"cena": 1.0, "kategorija": "DEPILACIJA", "naziv": "primer", "trajanjeMin": 1, "paket_ids": [1], "radnik_ids": [1], "termin_ids": [1]}')
    data["paket_ids"] = []
    data["radnik_ids"] = []
    data["termin_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Usluga"] = data
    obj = repo.create_usluga(db, schema.UslugaCreate(**data))
    created_ids["Usluga"] = obj.id
    print("Kreiran(a) Usluga id=", obj.id)
    data = json.loads('{"datumVreme": "2026-09-10T10:00:00", "status": "ODRZAN", "trajanjeMin": 1, "klijent_id": 1, "radnik_id": 1, "usluga_ids": [1]}')
    data["klijent_id"] = created_ids["Klijent"]
    data["radnik_id"] = created_ids["Radnik"]
    data["usluga_ids"] = []
    # Pydantic converts ISO dates/times and enum values for the repository.
    payloads["Termin"] = data
    obj = repo.create_termin(db, schema.TerminCreate(**data))
    created_ids["Termin"] = obj.id
    print("Kreiran(a) Termin id=", obj.id)

    print("--- Prolaz 2: uspostavljanje N:N veza ---")
    data = dict(payloads["Paket"])
    data["usluga_ids"] = [created_ids["Usluga"]]
    repo.update_paket(db, created_ids["Paket"], schema.PaketCreate(**data))
    print("Povezane N:N veze: Paket")
    data = dict(payloads["Radnik"])
    data["usluga_ids"] = [created_ids["Usluga"]]
    repo.update_radnik(db, created_ids["Radnik"], schema.RadnikCreate(**data))
    print("Povezane N:N veze: Radnik")
    data = dict(payloads["Usluga"])
    data["paket_ids"] = [created_ids["Paket"]]
    data["radnik_ids"] = [created_ids["Radnik"]]
    data["termin_ids"] = [created_ids["Termin"]]
    repo.update_usluga(db, created_ids["Usluga"], schema.UslugaCreate(**data))
    print("Povezane N:N veze: Usluga")
    data = dict(payloads["Termin"])
    data["usluga_ids"] = [created_ids["Usluga"]]
    repo.update_termin(db, created_ids["Termin"], schema.TerminCreate(**data))
    print("Povezane N:N veze: Termin")
    return created_ids


def main():
    parser = argparse.ArgumentParser(description="Insert example records and N:N links")
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
        print("Seed podaci uspesno ubaceni.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()