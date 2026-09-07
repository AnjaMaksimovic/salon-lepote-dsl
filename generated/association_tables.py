"""Generated from model/salon_model.py; update the model or template before regenerating."""
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from generated.entities import Base
from generated.entities import Client
from generated.entities import Package
from generated.entities import Worker
from generated.entities import Appointment
from generated.entities import Service

service_package = Table(
    "service_package",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("service.id"), primary_key=True),
    Column("package_id", Integer, ForeignKey("package.id"), primary_key=True),
)

service_worker = Table(
    "service_worker",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("service.id"), primary_key=True),
    Column("worker_id", Integer, ForeignKey("worker.id"), primary_key=True),
)

service_appointment = Table(
    "service_appointment",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("service.id"), primary_key=True),
    Column("appointment_id", Integer, ForeignKey("appointment.id"), primary_key=True),
)


Service.package = relationship(
    "Package", secondary=service_package, back_populates="service"
)
Package.service = relationship(
    "Service", secondary=service_package, back_populates="package"
)
Service.worker = relationship(
    "Worker", secondary=service_worker, back_populates="service"
)
Worker.service = relationship(
    "Service", secondary=service_worker, back_populates="worker"
)
Service.appointment = relationship(
    "Appointment", secondary=service_appointment, back_populates="service"
)
Appointment.service = relationship(
    "Service", secondary=service_appointment, back_populates="appointment"
)
