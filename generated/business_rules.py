"""
Poslovna pravila - rucno implementirane OCL invarijante iz model/salon_model.py.

Ovaj fajl se NE generise iz modela (za razliku od ostalih .j2 sablona) - ne
postoji generican nacin da se 3 konkretne domenske provere izvedu iz proizvoljnog
B-UML modela, pa su implementirane direktno u Python-u, sa istim imenima i
semantikom kao odgovarajuci OCL izrazi. generate.py samo kopira ovaj fajl u
generated/business_rules.py, bez Jinja2 obrade.
"""
from typing import Iterable, List

from sqlalchemy.orm import Session

from generated.entities import Usluga
from generated.repository import get_radnik_usluga_ids


class BusinessRuleViolation(ValueError):
    """Podignuto kada neko poslovno pravilo (OCL invarijanta) nije zadovoljeno."""


def _usluge_by_ids(db: Session, usluga_ids: Iterable[int]) -> List[Usluga]:
    ids = list(usluga_ids)
    if not ids:
        return []
    objs = db.query(Usluga).filter(Usluga.id.in_(ids)).all()
    missing = set(ids) - {o.id for o in objs}
    if missing:
        raise BusinessRuleViolation(f"Usluga(e) sa id {sorted(missing)} ne postoje.")
    return objs


def check_trajanje_dovoljno(trajanje_min: int, usluga_ids: Iterable[int], db: Session) -> None:
    """
    context Termin inv TrajanjeDovoljno:
        self.trajanjeMin >= self.usluga->collect(u | u.trajanjeMin)->sum()
    Trajanje termina mora biti dovoljno da pokrije sve zakazane usluge.
    """
    ukupno = sum(u.trajanjeMin for u in _usluge_by_ids(db, usluga_ids))
    if trajanje_min < ukupno:
        raise BusinessRuleViolation(
            f"Trajanje termina ({trajanje_min} min) je manje od zbira trajanja "
            f"zakazanih usluga ({ukupno} min)."
        )


def check_usluga_kompatibilna_sa_radnikom(radnik_id: int, usluga_ids: Iterable[int], db: Session) -> None:
    """
    context Termin inv UslugaKompatibilnaSaRadnikom:
        self.usluga->forAll(u | self.radnik.usluga->includes(u))
    Usluge zakazane u terminu moraju biti u okviru specijalizacija dodeljenog radnika.
    """
    radnikove_usluge = set(get_radnik_usluga_ids(db, radnik_id))
    nedozvoljene = set(usluga_ids) - radnikove_usluge
    if nedozvoljene:
        raise BusinessRuleViolation(
            f"Usluga(e) sa id {sorted(nedozvoljene)} nisu u okviru specijalizacija radnika {radnik_id}."
        )


def check_paket_jeftiniji_od_pojedinacnih(cena: float, usluga_ids: Iterable[int], db: Session) -> None:
    """
    context Paket inv PaketJeftinijiOdPojedinacnih:
        self.cena < self.usluga->collect(u | u.cena)->sum()
    Cena paketa mora biti niza od zbira cena pojedinacnih usluga koje sadrzi.
    """
    ukupno = sum(u.cena for u in _usluge_by_ids(db, usluga_ids))
    if not (cena < ukupno):
        raise BusinessRuleViolation(
            f"Cena paketa ({cena}) mora biti niza od zbira cena usluga u paketu ({ukupno})."
        )
