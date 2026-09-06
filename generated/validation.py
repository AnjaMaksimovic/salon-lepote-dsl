"""AUTO-GENERISANO - NE MENJATI RUČNO.
Izmene radite u model/salon_model.py i ponovo pokrenite generate.py.
OCL ograničenja se proveravaju nad podacima zahteva pre upisa u bazu.
Povezani objekti učitavaju se iz baze na osnovu ID vrednosti iz zahteva.
"""
from sqlalchemy.orm import Session
from generated.entities import Klijent, Paket, Radnik, Termin, Usluga

def validiraj_PaketJeftinijiOdPojedinacnih(db: Session, data) -> None:
    """Cena paketa mora biti niža od zbira cena pojedinačnih usluga koje sadrži.

    Izvorno OCL ograničenje:
    context Paket inv PaketJeftinijiOdPojedinacnih:   self.cena < self.usluga->collect(u | u.cena)->sum()
    """
    povezani = db.query(Usluga).filter(Usluga.id.in_(data.usluga_ids)).all()
    zbir = sum(getattr(o, "cena") for o in povezani)
    if not (data.cena < zbir):
        raise ValueError('Cena paketa mora biti niža od zbira cena pojedinačnih usluga koje sadrži.')


def validiraj_TrajanjeDovoljno(db: Session, data) -> None:
    """Trajanje termina mora biti dovoljno da pokrije sve zakazane usluge.

    Izvorno OCL ograničenje:
    context Termin inv TrajanjeDovoljno:   self.trajanjeMin >= self.usluga->collect(u | u.trajanjeMin)->sum()
    """
    povezani = db.query(Usluga).filter(Usluga.id.in_(data.usluga_ids)).all()
    zbir = sum(getattr(o, "trajanjeMin") for o in povezani)
    if not (data.trajanjeMin >= zbir):
        raise ValueError('Trajanje termina mora biti dovoljno da pokrije sve zakazane usluge.')


def validiraj_UslugaKompatibilnaSaRadnikom(db: Session, data) -> None:
    """Usluge zakazane u terminu moraju biti u okviru specijalizacija dodeljenog radnika.

    Izvorno OCL ograničenje:
    context Termin inv UslugaKompatibilnaSaRadnikom:   self.usluga->forAll(u | self.radnik.usluga->includes(u))
    """
    drugi_objekat = db.query(Radnik).filter(Radnik.id == data.radnik_id).first()
    dozvoljeni_ids = {u.id for u in getattr(drugi_objekat, "usluga")} if drugi_objekat else set()
    if not all(uid in dozvoljeni_ids for uid in data.usluga_ids):
        raise ValueError('Usluge zakazane u terminu moraju biti u okviru specijalizacija dodeljenog radnika.')


def validiraj_Paket(db: Session, data) -> None:
    """Proverava sva OCL ograničenja definisana za Paket."""
    validiraj_PaketJeftinijiOdPojedinacnih(db, data)

def validiraj_Termin(db: Session, data) -> None:
    """Proverava sva OCL ograničenja definisana za Termin."""
    validiraj_TrajanjeDovoljno(db, data)
    validiraj_UslugaKompatibilnaSaRadnikom(db, data)

