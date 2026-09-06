"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel
from generated.enums import KategorijaUsluge, StatusTermina


class KlijentBase(BaseModel):
    email: str
    ime: str
    telefon: str


class KlijentCreate(KlijentBase):
    pass


class KlijentOut(KlijentBase):
    id: int

    class Config:
        from_attributes = True

class PaketBase(BaseModel):
    cena: float
    naziv: str


class PaketCreate(PaketBase):
    usluga_ids: List[int] = []


class PaketOut(PaketBase):
    id: int

    class Config:
        from_attributes = True

class RadnikBase(BaseModel):
    ime: str
    prezime: str
    radnoVremeDo: time
    radnoVremeOd: time


class RadnikCreate(RadnikBase):
    usluga_ids: List[int] = []


class RadnikOut(RadnikBase):
    id: int

    class Config:
        from_attributes = True

class TerminBase(BaseModel):
    datumVreme: datetime
    status: StatusTermina
    trajanjeMin: int


class TerminCreate(TerminBase):
    klijent_id: int
    radnik_id: int
    usluga_ids: List[int] = []


class TerminOut(TerminBase):
    id: int
    klijent_id: int
    radnik_id: int

    class Config:
        from_attributes = True

class UslugaBase(BaseModel):
    cena: float
    kategorija: KategorijaUsluge
    naziv: str
    trajanjeMin: int


class UslugaCreate(UslugaBase):
    paket_ids: List[int] = []
    radnik_ids: List[int] = []
    termin_ids: List[int] = []


class UslugaOut(UslugaBase):
    id: int

    class Config:
        from_attributes = True
