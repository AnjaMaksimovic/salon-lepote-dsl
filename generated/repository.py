"""Generated from model/salon_model.py; update the model or template before regenerating."""
from typing import List, Optional
from sqlalchemy import select, insert, delete as sa_delete
from sqlalchemy.orm import Session
from generated.entities import Client, Package, Worker, Appointment, Service
from generated.association_tables import service_package, service_worker, service_appointment
from generated.schema import ClientCreate, PackageCreate, WorkerCreate, AppointmentCreate, ServiceCreate
from generated.dto import ClientDTO, PackageDTO, WorkerDTO, AppointmentDTO, ServiceDTO
from generated.converter import client_to_dto, package_to_dto, worker_to_dto, appointment_to_dto, service_to_dto

# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def create_client(db: Session, data: ClientCreate) -> ClientDTO:
    obj = Client(
        email=data.email,
        name=data.name,
        phone=data.phone,
    )
    db.add(obj)
    db.flush()
    db.commit()
    db.refresh(obj)
    return client_to_dto(obj)


def get_client(db: Session, client_id: int) -> Optional[ClientDTO]:
    obj = db.get(Client, client_id)
    return client_to_dto(obj) if obj is not None else None


def list_client(db: Session) -> List[ClientDTO]:
    objs = db.execute(select(Client)).scalars().all()
    return [client_to_dto(o) for o in objs]


def update_client(db: Session, client_id: int, data: ClientCreate) -> Optional[ClientDTO]:
    obj = db.get(Client, client_id)
    if obj is None:
        return None
    obj.email = data.email
    obj.name = data.name
    obj.phone = data.phone
    db.commit()
    db.refresh(obj)
    return client_to_dto(obj)


def delete_client(db: Session, client_id: int) -> bool:
    obj = db.get(Client, client_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------

def create_package(db: Session, data: PackageCreate) -> PackageDTO:
    obj = Package(
        price=data.price,
        name=data.name,
    )
    db.add(obj)
    db.flush()
    for target_id in data.service_ids:
        db.execute(insert(service_package).values(package_id=obj.id, service_id=target_id))
    db.commit()
    db.refresh(obj)
    return package_to_dto(obj)


def get_package(db: Session, package_id: int) -> Optional[PackageDTO]:
    obj = db.get(Package, package_id)
    return package_to_dto(obj) if obj is not None else None


def list_package(db: Session) -> List[PackageDTO]:
    objs = db.execute(select(Package)).scalars().all()
    return [package_to_dto(o) for o in objs]


def update_package(db: Session, package_id: int, data: PackageCreate) -> Optional[PackageDTO]:
    obj = db.get(Package, package_id)
    if obj is None:
        return None
    obj.price = data.price
    obj.name = data.name
    db.execute(sa_delete(service_package).where(service_package.c.package_id == package_id))
    for target_id in data.service_ids:
        db.execute(insert(service_package).values(package_id=package_id, service_id=target_id))
    db.commit()
    db.refresh(obj)
    return package_to_dto(obj)


def delete_package(db: Session, package_id: int) -> bool:
    obj = db.get(Package, package_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_package_service_ids(db: Session, package_id: int) -> List[int]:
    rows = db.execute(
        select(service_package.c.service_id).where(service_package.c.package_id == package_id)
    ).scalars().all()
    return list(rows)

# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def create_worker(db: Session, data: WorkerCreate) -> WorkerDTO:
    obj = Worker(
        name=data.name,
        surname=data.surname,
        workingHoursTo=data.workingHoursTo,
        workingHoursFrom=data.workingHoursFrom,
    )
    db.add(obj)
    db.flush()
    for target_id in data.service_ids:
        db.execute(insert(service_worker).values(worker_id=obj.id, service_id=target_id))
    db.commit()
    db.refresh(obj)
    return worker_to_dto(obj)


def get_worker(db: Session, worker_id: int) -> Optional[WorkerDTO]:
    obj = db.get(Worker, worker_id)
    return worker_to_dto(obj) if obj is not None else None


def list_worker(db: Session) -> List[WorkerDTO]:
    objs = db.execute(select(Worker)).scalars().all()
    return [worker_to_dto(o) for o in objs]


def update_worker(db: Session, worker_id: int, data: WorkerCreate) -> Optional[WorkerDTO]:
    obj = db.get(Worker, worker_id)
    if obj is None:
        return None
    obj.name = data.name
    obj.surname = data.surname
    obj.workingHoursTo = data.workingHoursTo
    obj.workingHoursFrom = data.workingHoursFrom
    db.execute(sa_delete(service_worker).where(service_worker.c.worker_id == worker_id))
    for target_id in data.service_ids:
        db.execute(insert(service_worker).values(worker_id=worker_id, service_id=target_id))
    db.commit()
    db.refresh(obj)
    return worker_to_dto(obj)


def delete_worker(db: Session, worker_id: int) -> bool:
    obj = db.get(Worker, worker_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_worker_service_ids(db: Session, worker_id: int) -> List[int]:
    rows = db.execute(
        select(service_worker.c.service_id).where(service_worker.c.worker_id == worker_id)
    ).scalars().all()
    return list(rows)

# ---------------------------------------------------------------------------
# Appointment
# ---------------------------------------------------------------------------

def create_appointment(db: Session, data: AppointmentCreate) -> AppointmentDTO:
    obj = Appointment(
        dateTime=data.dateTime,
        status=data.status,
        durationMinutes=data.durationMinutes,
        client_id=data.client_id,
        worker_id=data.worker_id,
    )
    db.add(obj)
    db.flush()
    for target_id in data.service_ids:
        db.execute(insert(service_appointment).values(appointment_id=obj.id, service_id=target_id))
    db.commit()
    db.refresh(obj)
    return appointment_to_dto(obj)


def get_appointment(db: Session, appointment_id: int) -> Optional[AppointmentDTO]:
    obj = db.get(Appointment, appointment_id)
    return appointment_to_dto(obj) if obj is not None else None


def list_appointment(db: Session) -> List[AppointmentDTO]:
    objs = db.execute(select(Appointment)).scalars().all()
    return [appointment_to_dto(o) for o in objs]


def update_appointment(db: Session, appointment_id: int, data: AppointmentCreate) -> Optional[AppointmentDTO]:
    obj = db.get(Appointment, appointment_id)
    if obj is None:
        return None
    obj.dateTime = data.dateTime
    obj.status = data.status
    obj.durationMinutes = data.durationMinutes
    obj.client_id = data.client_id
    obj.worker_id = data.worker_id
    db.execute(sa_delete(service_appointment).where(service_appointment.c.appointment_id == appointment_id))
    for target_id in data.service_ids:
        db.execute(insert(service_appointment).values(appointment_id=appointment_id, service_id=target_id))
    db.commit()
    db.refresh(obj)
    return appointment_to_dto(obj)


def delete_appointment(db: Session, appointment_id: int) -> bool:
    obj = db.get(Appointment, appointment_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_appointment_service_ids(db: Session, appointment_id: int) -> List[int]:
    rows = db.execute(
        select(service_appointment.c.service_id).where(service_appointment.c.appointment_id == appointment_id)
    ).scalars().all()
    return list(rows)

# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

def create_service(db: Session, data: ServiceCreate) -> ServiceDTO:
    obj = Service(
        price=data.price,
        category=data.category,
        name=data.name,
        durationMinutes=data.durationMinutes,
    )
    db.add(obj)
    db.flush()
    for target_id in data.package_ids:
        db.execute(insert(service_package).values(service_id=obj.id, package_id=target_id))
    for target_id in data.worker_ids:
        db.execute(insert(service_worker).values(service_id=obj.id, worker_id=target_id))
    for target_id in data.appointment_ids:
        db.execute(insert(service_appointment).values(service_id=obj.id, appointment_id=target_id))
    db.commit()
    db.refresh(obj)
    return service_to_dto(obj)


def get_service(db: Session, service_id: int) -> Optional[ServiceDTO]:
    obj = db.get(Service, service_id)
    return service_to_dto(obj) if obj is not None else None


def list_service(db: Session) -> List[ServiceDTO]:
    objs = db.execute(select(Service)).scalars().all()
    return [service_to_dto(o) for o in objs]


def update_service(db: Session, service_id: int, data: ServiceCreate) -> Optional[ServiceDTO]:
    obj = db.get(Service, service_id)
    if obj is None:
        return None
    obj.price = data.price
    obj.category = data.category
    obj.name = data.name
    obj.durationMinutes = data.durationMinutes
    db.execute(sa_delete(service_package).where(service_package.c.service_id == service_id))
    for target_id in data.package_ids:
        db.execute(insert(service_package).values(service_id=service_id, package_id=target_id))
    db.execute(sa_delete(service_worker).where(service_worker.c.service_id == service_id))
    for target_id in data.worker_ids:
        db.execute(insert(service_worker).values(service_id=service_id, worker_id=target_id))
    db.execute(sa_delete(service_appointment).where(service_appointment.c.service_id == service_id))
    for target_id in data.appointment_ids:
        db.execute(insert(service_appointment).values(service_id=service_id, appointment_id=target_id))
    db.commit()
    db.refresh(obj)
    return service_to_dto(obj)


def delete_service(db: Session, service_id: int) -> bool:
    obj = db.get(Service, service_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_service_package_ids(db: Session, service_id: int) -> List[int]:
    rows = db.execute(
        select(service_package.c.package_id).where(service_package.c.service_id == service_id)
    ).scalars().all()
    return list(rows)

def get_service_worker_ids(db: Session, service_id: int) -> List[int]:
    rows = db.execute(
        select(service_worker.c.worker_id).where(service_worker.c.service_id == service_id)
    ).scalars().all()
    return list(rows)

def get_service_appointment_ids(db: Session, service_id: int) -> List[int]:
    rows = db.execute(
        select(service_appointment.c.appointment_id).where(service_appointment.c.service_id == service_id)
    ).scalars().all()
    return list(rows)
