"""Generated from model/salon_model.py; update the model or template before regenerating."""
from dataclasses import dataclass
from datetime import date, datetime, time
from generated.enums import ServiceCategory, AppointmentStatus


@dataclass
class ClientDTO:
    id: int
    email: str
    name: str
    phone: str

@dataclass
class PackageDTO:
    id: int
    price: float
    name: str

@dataclass
class WorkerDTO:
    id: int
    name: str
    surname: str
    workingHoursTo: time
    workingHoursFrom: time

@dataclass
class AppointmentDTO:
    id: int
    dateTime: datetime
    status: AppointmentStatus
    durationMinutes: int
    client_id: int
    worker_id: int

@dataclass
class ServiceDTO:
    id: int
    price: float
    category: ServiceCategory
    name: str
    durationMinutes: int
