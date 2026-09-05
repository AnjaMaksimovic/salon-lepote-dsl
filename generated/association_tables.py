"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from generated.entities import Base

termin_usluga = Table(
    "termin_usluga",
    Base.metadata,
    Column("usluga_id", Integer, ForeignKey("usluga.id"), primary_key=True),
    Column("termin_id", Integer, ForeignKey("termin.id"), primary_key=True),
)

radnik_usluga = Table(
    "radnik_usluga",
    Base.metadata,
    Column("usluga_id", Integer, ForeignKey("usluga.id"), primary_key=True),
    Column("radnik_id", Integer, ForeignKey("radnik.id"), primary_key=True),
)

paket_usluga = Table(
    "paket_usluga",
    Base.metadata,
    Column("usluga_id", Integer, ForeignKey("usluga.id"), primary_key=True),
    Column("paket_id", Integer, ForeignKey("paket.id"), primary_key=True),
)

