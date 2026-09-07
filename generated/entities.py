"""Generated from model/salon_model.py; update the model or template before regenerating."""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Time, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, relationship
from generated.enums import ServiceCategory, AppointmentStatus


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    name = Column(String(100))
    phone = Column(String(100))
    appointment = relationship("Appointment", back_populates="client")

class Package(Base):
    __tablename__ = "package"
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    name = Column(String(100))

class Worker(Base):
    __tablename__ = "worker"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    surname = Column(String(100))
    workingHoursTo = Column(Time)
    workingHoursFrom = Column(Time)
    appointment = relationship("Appointment", back_populates="worker")

class Appointment(Base):
    __tablename__ = "appointment"
    id = Column(Integer, primary_key=True)
    dateTime = Column(DateTime)
    status = Column(SAEnum(AppointmentStatus))
    durationMinutes = Column(Integer)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("worker.id"), nullable=False)
    client = relationship("Client", back_populates="appointment")
    worker = relationship("Worker", back_populates="appointment")

class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    category = Column(SAEnum(ServiceCategory))
    name = Column(String(100))
    durationMinutes = Column(Integer)
