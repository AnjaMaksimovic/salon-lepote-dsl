"""Request and response schemas for the generated API."""
from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from generated.enums import ServiceCategory, AppointmentStatus

class ClientRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    phone: str

class PackageRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    price: float
    name: str

class WorkerRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    surname: str
    workingHoursTo: time
    workingHoursFrom: time

class AppointmentRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    dateTime: datetime
    status: AppointmentStatus
    durationMinutes: int

class ServiceRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    price: float
    category: ServiceCategory
    name: str
    durationMinutes: int

class ClientBase(BaseModel):
    email: str
    name: str
    phone: str


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ClientUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


ClientOut = ClientRead
class PackageBase(BaseModel):
    price: float
    name: str


class PackageCreate(PackageBase):
    service_ids: list[int] = Field(default_factory=list)


class PackageRead(PackageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    service: list[ServiceRef] = Field(default_factory=list)


class PackageUpdate(BaseModel):
    price: Optional[float] = None
    name: Optional[str] = None
    service_ids: Optional[list[int]] = None


PackageOut = PackageRead
class WorkerBase(BaseModel):
    name: str
    surname: str
    workingHoursTo: time
    workingHoursFrom: time


class WorkerCreate(WorkerBase):
    service_ids: list[int] = Field(default_factory=list)


class WorkerRead(WorkerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    service: list[ServiceRef] = Field(default_factory=list)


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    workingHoursTo: Optional[time] = None
    workingHoursFrom: Optional[time] = None
    service_ids: Optional[list[int]] = None


WorkerOut = WorkerRead
class AppointmentBase(BaseModel):
    dateTime: datetime
    status: AppointmentStatus
    durationMinutes: int


class AppointmentCreate(AppointmentBase):
    client_id: int
    worker_id: int
    service_ids: list[int] = Field(default_factory=list)


class AppointmentRead(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    client_id: int
    worker_id: int
    service: list[ServiceRef] = Field(default_factory=list)


class AppointmentUpdate(BaseModel):
    dateTime: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    durationMinutes: Optional[int] = None
    client_id: Optional[int] = None
    worker_id: Optional[int] = None
    service_ids: Optional[list[int]] = None


AppointmentOut = AppointmentRead
class ServiceBase(BaseModel):
    price: float
    category: ServiceCategory
    name: str
    durationMinutes: int


class ServiceCreate(ServiceBase):
    package_ids: list[int] = Field(default_factory=list)
    worker_ids: list[int] = Field(default_factory=list)
    appointment_ids: list[int] = Field(default_factory=list)


class ServiceRead(ServiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    package: list[PackageRef] = Field(default_factory=list)
    worker: list[WorkerRef] = Field(default_factory=list)
    appointment: list[AppointmentRef] = Field(default_factory=list)


class ServiceUpdate(BaseModel):
    price: Optional[float] = None
    category: Optional[ServiceCategory] = None
    name: Optional[str] = None
    durationMinutes: Optional[int] = None
    package_ids: Optional[list[int]] = None
    worker_ids: Optional[list[int]] = None
    appointment_ids: Optional[list[int]] = None


ServiceOut = ServiceRead
