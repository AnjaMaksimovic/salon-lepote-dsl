"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from dataclasses import dataclass
from datetime import date, datetime, time
from generated.enums import KategorijaUsluge, StatusTermina


@dataclass
class KlijentDTO:
    id: int
    email: str
    ime: str
    telefon: str

@dataclass
class PaketDTO:
    id: int
    cena: float
    naziv: str

@dataclass
class RadnikDTO:
    id: int
    ime: str
    prezime: str
    radnoVremeDo: time
    radnoVremeOd: time

@dataclass
class TerminDTO:
    id: int
    datumVreme: datetime
    status: StatusTermina
    trajanjeMin: int
    klijent_id: int
    radnik_id: int

@dataclass
class UslugaDTO:
    id: int
    cena: float
    kategorija: KategorijaUsluge
    naziv: str
    trajanjeMin: int
