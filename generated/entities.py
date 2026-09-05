"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Time, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, relationship
from generated.enums import KategorijaUsluge, StatusTermina


class Base(DeclarativeBase):
    pass


class Paket(Base):
    __tablename__ = "paket"
    id = Column(Integer, primary_key=True)
    cena = Column(Float)
    naziv = Column(String(100))

class Usluga(Base):
    __tablename__ = "usluga"
    id = Column(Integer, primary_key=True)
    cena = Column(Float)
    naziv = Column(String(100))
    kategorija = Column(SAEnum(KategorijaUsluge))
    trajanjeMin = Column(Integer)

class Termin(Base):
    __tablename__ = "termin"
    id = Column(Integer, primary_key=True)
    trajanjeMin = Column(Integer)
    status = Column(SAEnum(StatusTermina))
    datumVreme = Column(DateTime)
    radnik_id = Column(Integer, ForeignKey("radnik.id"), nullable=False)
    klijent_id = Column(Integer, ForeignKey("klijent.id"), nullable=False)
    radnik = relationship("Radnik", back_populates="termin")
    klijent = relationship("Klijent", back_populates="termin")

class Klijent(Base):
    __tablename__ = "klijent"
    id = Column(Integer, primary_key=True)
    ime = Column(String(100))
    telefon = Column(String(100))
    email = Column(String(100))
    termin = relationship("Termin", back_populates="klijent")

class Radnik(Base):
    __tablename__ = "radnik"
    id = Column(Integer, primary_key=True)
    prezime = Column(String(100))
    ime = Column(String(100))
    radnoVremeDo = Column(Time)
    radnoVremeOd = Column(Time)
    termin = relationship("Termin", back_populates="radnik")
