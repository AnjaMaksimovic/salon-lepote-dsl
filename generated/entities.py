from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Time
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Klijent(Base):
    __tablename__ = "klijent"
    id = Column(Integer, primary_key=True)

    telefon = Column(String(100))

    ime = Column(String(100))

    email = Column(String(100))
