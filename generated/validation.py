"""Generated from model/salon_model.py; update the model or template before regenerating."""
from sqlalchemy.orm import Session
from generated.entities import Client, Package, Worker, Appointment, Service

def validate_PackageDiscount(db: Session, data) -> None:
    """The package price must be lower than the total price of its services.

    Source OCL constraint:
    context Package inv PackageDiscount:   self.price < self.service->collect(u | u.price)->sum()
    """
    related = db.query(Service).filter(Service.id.in_(data.service_ids)).all()
    total = sum(getattr(o, "price") for o in related)
    if not (data.price < total):
        raise ValueError('The package price must be lower than the total price of its services.')


def validate_SufficientDuration(db: Session, data) -> None:
    """The appointment must be long enough to cover all selected services.

    Source OCL constraint:
    context Appointment inv SufficientDuration:   self.durationMinutes >= self.service->collect(u | u.durationMinutes)->sum()
    """
    related = db.query(Service).filter(Service.id.in_(data.service_ids)).all()
    total = sum(getattr(o, "durationMinutes") for o in related)
    if not (data.durationMinutes >= total):
        raise ValueError('The appointment must be long enough to cover all selected services.')


def validate_WorkerServiceCompatibility(db: Session, data) -> None:
    """The selected worker must be qualified to perform every selected service.

    Source OCL constraint:
    context Appointment inv WorkerServiceCompatibility:   self.service->forAll(u | self.worker.service->includes(u))
    """
    related_object = db.query(Worker).filter(Worker.id == data.worker_id).first()
    allowed_ids = {u.id for u in getattr(related_object, "service")} if related_object else set()
    if not all(uid in allowed_ids for uid in data.service_ids):
        raise ValueError('The selected worker must be qualified to perform every selected service.')


def validate_Package(db: Session, data) -> None:
    """Validates all OCL constraints for Package."""
    validate_PackageDiscount(db, data)

def validate_Appointment(db: Session, data) -> None:
    """Validates all OCL constraints for Appointment."""
    validate_SufficientDuration(db, data)
    validate_WorkerServiceCompatibility(db, data)

