"""CRUD endpoints with reference and business-rule validation."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from generated.database import get_db
from generated import repository as repo, entities, schema, validation

router = APIRouter()


def write_record(db, operation):
    try:
        return operation()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Record is referenced or contains invalid relationships") from error


def validate_client(db, data):
    return data


@router.post("/client/", response_model=schema.ClientRead)
def create_client(data: schema.ClientCreate, db: Session = Depends(get_db)):
    validate_client(db, data)
    obj = write_record(db, lambda: repo.create_client(db, data))
    return db.get(entities.Client, obj.id)


@router.get("/client/", response_model=list[schema.ClientRead])
def list_client(db: Session = Depends(get_db)):
    return db.query(entities.Client).order_by(entities.Client.id).all()


@router.get("/client/{item_id}", response_model=schema.ClientRead)
def get_client(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(entities.Client, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return obj


@router.put("/client/{item_id}", response_model=schema.ClientRead)
def update_client(item_id: int, data: schema.ClientUpdate, db: Session = Depends(get_db)):
    obj = get_client(item_id, db)
    current = {
        "email": obj.email,
        "name": obj.name,
        "phone": obj.phone,
    }
    current.update(data.model_dump(exclude_unset=True))
    try:
        merged = schema.ClientCreate(**current)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail="Update contains invalid or null fields") from error
    validate_client(db, merged)
    write_record(db, lambda: repo.update_client(db, item_id, merged))
    return db.get(entities.Client, item_id)


@router.delete("/client/{item_id}")
def delete_client(item_id: int, db: Session = Depends(get_db)):
    if not write_record(db, lambda: repo.delete_client(db, item_id)):
        raise HTTPException(status_code=404, detail="Client not found")
    return {"deleted": True}

def validate_package(db, data):
    data.service_ids = list(dict.fromkeys(data.service_ids))
    for item_id in data.service_ids:
        if db.get(entities.Service, item_id) is None:
            raise HTTPException(status_code=400, detail="Unknown service ID")
    try:
        validation.validate_Package(db, data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return data


@router.post("/package/", response_model=schema.PackageRead)
def create_package(data: schema.PackageCreate, db: Session = Depends(get_db)):
    validate_package(db, data)
    obj = write_record(db, lambda: repo.create_package(db, data))
    return db.get(entities.Package, obj.id)


@router.get("/package/", response_model=list[schema.PackageRead])
def list_package(db: Session = Depends(get_db)):
    return db.query(entities.Package).order_by(entities.Package.id).all()


@router.get("/package/{item_id}", response_model=schema.PackageRead)
def get_package(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(entities.Package, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return obj


@router.put("/package/{item_id}", response_model=schema.PackageRead)
def update_package(item_id: int, data: schema.PackageUpdate, db: Session = Depends(get_db)):
    obj = get_package(item_id, db)
    current = {
        "price": obj.price,
        "name": obj.name,
        "service_ids": repo.get_package_service_ids(db, item_id),
    }
    current.update(data.model_dump(exclude_unset=True))
    try:
        merged = schema.PackageCreate(**current)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail="Update contains invalid or null fields") from error
    validate_package(db, merged)
    write_record(db, lambda: repo.update_package(db, item_id, merged))
    return db.get(entities.Package, item_id)


@router.delete("/package/{item_id}")
def delete_package(item_id: int, db: Session = Depends(get_db)):
    if not write_record(db, lambda: repo.delete_package(db, item_id)):
        raise HTTPException(status_code=404, detail="Package not found")
    return {"deleted": True}

def validate_worker(db, data):
    data.service_ids = list(dict.fromkeys(data.service_ids))
    for item_id in data.service_ids:
        if db.get(entities.Service, item_id) is None:
            raise HTTPException(status_code=400, detail="Unknown service ID")
    return data


@router.post("/worker/", response_model=schema.WorkerRead)
def create_worker(data: schema.WorkerCreate, db: Session = Depends(get_db)):
    validate_worker(db, data)
    obj = write_record(db, lambda: repo.create_worker(db, data))
    return db.get(entities.Worker, obj.id)


@router.get("/worker/", response_model=list[schema.WorkerRead])
def list_worker(db: Session = Depends(get_db)):
    return db.query(entities.Worker).order_by(entities.Worker.id).all()


@router.get("/worker/{item_id}", response_model=schema.WorkerRead)
def get_worker(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(entities.Worker, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return obj


@router.put("/worker/{item_id}", response_model=schema.WorkerRead)
def update_worker(item_id: int, data: schema.WorkerUpdate, db: Session = Depends(get_db)):
    obj = get_worker(item_id, db)
    current = {
        "name": obj.name,
        "surname": obj.surname,
        "workingHoursTo": obj.workingHoursTo,
        "workingHoursFrom": obj.workingHoursFrom,
        "service_ids": repo.get_worker_service_ids(db, item_id),
    }
    current.update(data.model_dump(exclude_unset=True))
    try:
        merged = schema.WorkerCreate(**current)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail="Update contains invalid or null fields") from error
    validate_worker(db, merged)
    write_record(db, lambda: repo.update_worker(db, item_id, merged))
    return db.get(entities.Worker, item_id)


@router.delete("/worker/{item_id}")
def delete_worker(item_id: int, db: Session = Depends(get_db)):
    if not write_record(db, lambda: repo.delete_worker(db, item_id)):
        raise HTTPException(status_code=404, detail="Worker not found")
    return {"deleted": True}

def validate_appointment(db, data):
    if db.get(entities.Client, data.client_id) is None:
        raise HTTPException(status_code=400, detail="Unknown client_id")
    if db.get(entities.Worker, data.worker_id) is None:
        raise HTTPException(status_code=400, detail="Unknown worker_id")
    data.service_ids = list(dict.fromkeys(data.service_ids))
    for item_id in data.service_ids:
        if db.get(entities.Service, item_id) is None:
            raise HTTPException(status_code=400, detail="Unknown service ID")
    try:
        validation.validate_Appointment(db, data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return data


@router.post("/appointment/", response_model=schema.AppointmentRead)
def create_appointment(data: schema.AppointmentCreate, db: Session = Depends(get_db)):
    validate_appointment(db, data)
    obj = write_record(db, lambda: repo.create_appointment(db, data))
    return db.get(entities.Appointment, obj.id)


@router.get("/appointment/", response_model=list[schema.AppointmentRead])
def list_appointment(db: Session = Depends(get_db)):
    return db.query(entities.Appointment).order_by(entities.Appointment.id).all()


@router.get("/appointment/{item_id}", response_model=schema.AppointmentRead)
def get_appointment(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(entities.Appointment, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return obj


@router.put("/appointment/{item_id}", response_model=schema.AppointmentRead)
def update_appointment(item_id: int, data: schema.AppointmentUpdate, db: Session = Depends(get_db)):
    obj = get_appointment(item_id, db)
    current = {
        "dateTime": obj.dateTime,
        "status": obj.status,
        "durationMinutes": obj.durationMinutes,
        "client_id": obj.client_id,
        "worker_id": obj.worker_id,
        "service_ids": repo.get_appointment_service_ids(db, item_id),
    }
    current.update(data.model_dump(exclude_unset=True))
    try:
        merged = schema.AppointmentCreate(**current)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail="Update contains invalid or null fields") from error
    validate_appointment(db, merged)
    write_record(db, lambda: repo.update_appointment(db, item_id, merged))
    return db.get(entities.Appointment, item_id)


@router.delete("/appointment/{item_id}")
def delete_appointment(item_id: int, db: Session = Depends(get_db)):
    if not write_record(db, lambda: repo.delete_appointment(db, item_id)):
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"deleted": True}

def validate_service(db, data):
    data.package_ids = list(dict.fromkeys(data.package_ids))
    for item_id in data.package_ids:
        if db.get(entities.Package, item_id) is None:
            raise HTTPException(status_code=400, detail="Unknown package ID")
    data.worker_ids = list(dict.fromkeys(data.worker_ids))
    for item_id in data.worker_ids:
        if db.get(entities.Worker, item_id) is None:
            raise HTTPException(status_code=400, detail="Unknown worker ID")
    data.appointment_ids = list(dict.fromkeys(data.appointment_ids))
    for item_id in data.appointment_ids:
        if db.get(entities.Appointment, item_id) is None:
            raise HTTPException(status_code=400, detail="Unknown appointment ID")
    return data


@router.post("/service/", response_model=schema.ServiceRead)
def create_service(data: schema.ServiceCreate, db: Session = Depends(get_db)):
    validate_service(db, data)
    obj = write_record(db, lambda: repo.create_service(db, data))
    return db.get(entities.Service, obj.id)


@router.get("/service/", response_model=list[schema.ServiceRead])
def list_service(db: Session = Depends(get_db)):
    return db.query(entities.Service).order_by(entities.Service.id).all()


@router.get("/service/{item_id}", response_model=schema.ServiceRead)
def get_service(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(entities.Service, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return obj


@router.put("/service/{item_id}", response_model=schema.ServiceRead)
def update_service(item_id: int, data: schema.ServiceUpdate, db: Session = Depends(get_db)):
    obj = get_service(item_id, db)
    current = {
        "price": obj.price,
        "category": obj.category,
        "name": obj.name,
        "durationMinutes": obj.durationMinutes,
        "package_ids": repo.get_service_package_ids(db, item_id),
        "worker_ids": repo.get_service_worker_ids(db, item_id),
        "appointment_ids": repo.get_service_appointment_ids(db, item_id),
    }
    current.update(data.model_dump(exclude_unset=True))
    try:
        merged = schema.ServiceCreate(**current)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail="Update contains invalid or null fields") from error
    validate_service(db, merged)
    write_record(db, lambda: repo.update_service(db, item_id, merged))
    return db.get(entities.Service, item_id)


@router.delete("/service/{item_id}")
def delete_service(item_id: int, db: Session = Depends(get_db)):
    if not write_record(db, lambda: repo.delete_service(db, item_id)):
        raise HTTPException(status_code=404, detail="Service not found")
    return {"deleted": True}
