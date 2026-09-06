"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from generated.entities import Base

usluga_paket = Table(
    "usluga_paket",
    Base.metadata,
    Column("usluga_id", Integer, ForeignKey("usluga.id"), primary_key=True),
    Column("paket_id", Integer, ForeignKey("paket.id"), primary_key=True),
)

usluga_radnik = Table(
    "usluga_radnik",
    Base.metadata,
    Column("usluga_id", Integer, ForeignKey("usluga.id"), primary_key=True),
    Column("radnik_id", Integer, ForeignKey("radnik.id"), primary_key=True),
)

usluga_termin = Table(
    "usluga_termin",
    Base.metadata,
    Column("usluga_id", Integer, ForeignKey("usluga.id"), primary_key=True),
    Column("termin_id", Integer, ForeignKey("termin.id"), primary_key=True),
)

