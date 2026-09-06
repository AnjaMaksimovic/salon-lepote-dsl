"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel
from generated.enums import KategorijaUsluge, StatusTermina


class PaketBase(BaseModel):
    cena: float
    naziv: str


class PaketCreate(PaketBase):
    usluga_ids: List[int] = []


class PaketOut(PaketBase):
    id: int

    class Config:
        from_attributes = True

class UslugaBase(BaseModel):
    cena: float
    naziv: str
    kategorija: KategorijaUsluge
    trajanjeMin: int


class UslugaCreate(UslugaBase):
    pass


class UslugaOut(UslugaBase):
    id: int

    class Config:
        from_attributes = True

class TerminBase(BaseModel):
    trajanjeMin: int
    status: StatusTermina
    datumVreme: datetime


class TerminCreate(TerminBase):
    radnik_id: int
    klijent_id: int
    usluga_ids: List[int] = []


class TerminOut(TerminBase):
    id: int
    radnik_id: int
    klijent_id: int

    class Config:
        from_attributes = True

class KlijentBase(BaseModel):
    ime: str
    telefon: str
    email: str


class KlijentCreate(KlijentBase):
    pass


class KlijentOut(KlijentBase):
    id: int

    class Config:
        from_attributes = True

class RadnikBase(BaseModel):
    prezime: str
    ime: str
    radnoVremeDo: time
    radnoVremeOd: time


class RadnikCreate(RadnikBase):
    usluga_ids: List[int] = []


class RadnikOut(RadnikBase):
    id: int

    class Config:
        from_attributes = True
