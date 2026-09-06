"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from typing import List, Optional
from sqlalchemy import select, insert, delete as sa_delete
from sqlalchemy.orm import Session
from generated.entities import Klijent, Paket, Radnik, Termin, Usluga
from generated.association_tables import usluga_paket, usluga_radnik, usluga_termin
from generated.schema import KlijentCreate, PaketCreate, RadnikCreate, TerminCreate, UslugaCreate
from generated.dto import KlijentDTO, PaketDTO, RadnikDTO, TerminDTO, UslugaDTO
from generated.converter import klijent_to_dto, paket_to_dto, radnik_to_dto, termin_to_dto, usluga_to_dto

# ---------------------------------------------------------------------------
# Klijent
# ---------------------------------------------------------------------------

def create_klijent(db: Session, data: KlijentCreate) -> KlijentDTO:
    obj = Klijent(
        email=data.email,
        ime=data.ime,
        telefon=data.telefon,
    )
    db.add(obj)
    db.flush()
    db.commit()
    db.refresh(obj)
    return klijent_to_dto(obj)


def get_klijent(db: Session, klijent_id: int) -> Optional[KlijentDTO]:
    obj = db.get(Klijent, klijent_id)
    return klijent_to_dto(obj) if obj is not None else None


def list_klijent(db: Session) -> List[KlijentDTO]:
    objs = db.execute(select(Klijent)).scalars().all()
    return [klijent_to_dto(o) for o in objs]


def update_klijent(db: Session, klijent_id: int, data: KlijentCreate) -> Optional[KlijentDTO]:
    obj = db.get(Klijent, klijent_id)
    if obj is None:
        return None
    obj.email = data.email
    obj.ime = data.ime
    obj.telefon = data.telefon
    db.commit()
    db.refresh(obj)
    return klijent_to_dto(obj)


def delete_klijent(db: Session, klijent_id: int) -> bool:
    obj = db.get(Klijent, klijent_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

# ---------------------------------------------------------------------------
# Paket
# ---------------------------------------------------------------------------

def create_paket(db: Session, data: PaketCreate) -> PaketDTO:
    obj = Paket(
        cena=data.cena,
        naziv=data.naziv,
    )
    db.add(obj)
    db.flush()
    for target_id in data.usluga_ids:
        db.execute(insert(usluga_paket).values(paket_id=obj.id, usluga_id=target_id))
    db.commit()
    db.refresh(obj)
    return paket_to_dto(obj)


def get_paket(db: Session, paket_id: int) -> Optional[PaketDTO]:
    obj = db.get(Paket, paket_id)
    return paket_to_dto(obj) if obj is not None else None


def list_paket(db: Session) -> List[PaketDTO]:
    objs = db.execute(select(Paket)).scalars().all()
    return [paket_to_dto(o) for o in objs]


def update_paket(db: Session, paket_id: int, data: PaketCreate) -> Optional[PaketDTO]:
    obj = db.get(Paket, paket_id)
    if obj is None:
        return None
    obj.cena = data.cena
    obj.naziv = data.naziv
    db.execute(sa_delete(usluga_paket).where(usluga_paket.c.paket_id == paket_id))
    for target_id in data.usluga_ids:
        db.execute(insert(usluga_paket).values(paket_id=paket_id, usluga_id=target_id))
    db.commit()
    db.refresh(obj)
    return paket_to_dto(obj)


def delete_paket(db: Session, paket_id: int) -> bool:
    obj = db.get(Paket, paket_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_paket_usluga_ids(db: Session, paket_id: int) -> List[int]:
    rows = db.execute(
        select(usluga_paket.c.usluga_id).where(usluga_paket.c.paket_id == paket_id)
    ).scalars().all()
    return list(rows)

# ---------------------------------------------------------------------------
# Radnik
# ---------------------------------------------------------------------------

def create_radnik(db: Session, data: RadnikCreate) -> RadnikDTO:
    obj = Radnik(
        ime=data.ime,
        prezime=data.prezime,
        radnoVremeDo=data.radnoVremeDo,
        radnoVremeOd=data.radnoVremeOd,
    )
    db.add(obj)
    db.flush()
    for target_id in data.usluga_ids:
        db.execute(insert(usluga_radnik).values(radnik_id=obj.id, usluga_id=target_id))
    db.commit()
    db.refresh(obj)
    return radnik_to_dto(obj)


def get_radnik(db: Session, radnik_id: int) -> Optional[RadnikDTO]:
    obj = db.get(Radnik, radnik_id)
    return radnik_to_dto(obj) if obj is not None else None


def list_radnik(db: Session) -> List[RadnikDTO]:
    objs = db.execute(select(Radnik)).scalars().all()
    return [radnik_to_dto(o) for o in objs]


def update_radnik(db: Session, radnik_id: int, data: RadnikCreate) -> Optional[RadnikDTO]:
    obj = db.get(Radnik, radnik_id)
    if obj is None:
        return None
    obj.ime = data.ime
    obj.prezime = data.prezime
    obj.radnoVremeDo = data.radnoVremeDo
    obj.radnoVremeOd = data.radnoVremeOd
    db.execute(sa_delete(usluga_radnik).where(usluga_radnik.c.radnik_id == radnik_id))
    for target_id in data.usluga_ids:
        db.execute(insert(usluga_radnik).values(radnik_id=radnik_id, usluga_id=target_id))
    db.commit()
    db.refresh(obj)
    return radnik_to_dto(obj)


def delete_radnik(db: Session, radnik_id: int) -> bool:
    obj = db.get(Radnik, radnik_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_radnik_usluga_ids(db: Session, radnik_id: int) -> List[int]:
    rows = db.execute(
        select(usluga_radnik.c.usluga_id).where(usluga_radnik.c.radnik_id == radnik_id)
    ).scalars().all()
    return list(rows)

# ---------------------------------------------------------------------------
# Termin
# ---------------------------------------------------------------------------

def create_termin(db: Session, data: TerminCreate) -> TerminDTO:
    obj = Termin(
        datumVreme=data.datumVreme,
        status=data.status,
        trajanjeMin=data.trajanjeMin,
        klijent_id=data.klijent_id,
        radnik_id=data.radnik_id,
    )
    db.add(obj)
    db.flush()
    for target_id in data.usluga_ids:
        db.execute(insert(usluga_termin).values(termin_id=obj.id, usluga_id=target_id))
    db.commit()
    db.refresh(obj)
    return termin_to_dto(obj)


def get_termin(db: Session, termin_id: int) -> Optional[TerminDTO]:
    obj = db.get(Termin, termin_id)
    return termin_to_dto(obj) if obj is not None else None


def list_termin(db: Session) -> List[TerminDTO]:
    objs = db.execute(select(Termin)).scalars().all()
    return [termin_to_dto(o) for o in objs]


def update_termin(db: Session, termin_id: int, data: TerminCreate) -> Optional[TerminDTO]:
    obj = db.get(Termin, termin_id)
    if obj is None:
        return None
    obj.datumVreme = data.datumVreme
    obj.status = data.status
    obj.trajanjeMin = data.trajanjeMin
    obj.klijent_id = data.klijent_id
    obj.radnik_id = data.radnik_id
    db.execute(sa_delete(usluga_termin).where(usluga_termin.c.termin_id == termin_id))
    for target_id in data.usluga_ids:
        db.execute(insert(usluga_termin).values(termin_id=termin_id, usluga_id=target_id))
    db.commit()
    db.refresh(obj)
    return termin_to_dto(obj)


def delete_termin(db: Session, termin_id: int) -> bool:
    obj = db.get(Termin, termin_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_termin_usluga_ids(db: Session, termin_id: int) -> List[int]:
    rows = db.execute(
        select(usluga_termin.c.usluga_id).where(usluga_termin.c.termin_id == termin_id)
    ).scalars().all()
    return list(rows)

# ---------------------------------------------------------------------------
# Usluga
# ---------------------------------------------------------------------------

def create_usluga(db: Session, data: UslugaCreate) -> UslugaDTO:
    obj = Usluga(
        cena=data.cena,
        kategorija=data.kategorija,
        naziv=data.naziv,
        trajanjeMin=data.trajanjeMin,
    )
    db.add(obj)
    db.flush()
    for target_id in data.paket_ids:
        db.execute(insert(usluga_paket).values(usluga_id=obj.id, paket_id=target_id))
    for target_id in data.radnik_ids:
        db.execute(insert(usluga_radnik).values(usluga_id=obj.id, radnik_id=target_id))
    for target_id in data.termin_ids:
        db.execute(insert(usluga_termin).values(usluga_id=obj.id, termin_id=target_id))
    db.commit()
    db.refresh(obj)
    return usluga_to_dto(obj)


def get_usluga(db: Session, usluga_id: int) -> Optional[UslugaDTO]:
    obj = db.get(Usluga, usluga_id)
    return usluga_to_dto(obj) if obj is not None else None


def list_usluga(db: Session) -> List[UslugaDTO]:
    objs = db.execute(select(Usluga)).scalars().all()
    return [usluga_to_dto(o) for o in objs]


def update_usluga(db: Session, usluga_id: int, data: UslugaCreate) -> Optional[UslugaDTO]:
    obj = db.get(Usluga, usluga_id)
    if obj is None:
        return None
    obj.cena = data.cena
    obj.kategorija = data.kategorija
    obj.naziv = data.naziv
    obj.trajanjeMin = data.trajanjeMin
    db.execute(sa_delete(usluga_paket).where(usluga_paket.c.usluga_id == usluga_id))
    for target_id in data.paket_ids:
        db.execute(insert(usluga_paket).values(usluga_id=usluga_id, paket_id=target_id))
    db.execute(sa_delete(usluga_radnik).where(usluga_radnik.c.usluga_id == usluga_id))
    for target_id in data.radnik_ids:
        db.execute(insert(usluga_radnik).values(usluga_id=usluga_id, radnik_id=target_id))
    db.execute(sa_delete(usluga_termin).where(usluga_termin.c.usluga_id == usluga_id))
    for target_id in data.termin_ids:
        db.execute(insert(usluga_termin).values(usluga_id=usluga_id, termin_id=target_id))
    db.commit()
    db.refresh(obj)
    return usluga_to_dto(obj)


def delete_usluga(db: Session, usluga_id: int) -> bool:
    obj = db.get(Usluga, usluga_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_usluga_paket_ids(db: Session, usluga_id: int) -> List[int]:
    rows = db.execute(
        select(usluga_paket.c.paket_id).where(usluga_paket.c.usluga_id == usluga_id)
    ).scalars().all()
    return list(rows)

def get_usluga_radnik_ids(db: Session, usluga_id: int) -> List[int]:
    rows = db.execute(
        select(usluga_radnik.c.radnik_id).where(usluga_radnik.c.usluga_id == usluga_id)
    ).scalars().all()
    return list(rows)

def get_usluga_termin_ids(db: Session, usluga_id: int) -> List[int]:
    rows = db.execute(
        select(usluga_termin.c.termin_id).where(usluga_termin.c.usluga_id == usluga_id)
    ).scalars().all()
    return list(rows)
