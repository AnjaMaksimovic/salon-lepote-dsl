"""Manual checks for the domain model's service and package constraints."""
from sqlalchemy.orm import Session
from generated.entities import Service
from generated.repository import get_worker_service_ids


class BusinessRuleViolation(ValueError):
    """Raised when a request violates a business rule."""


def services_by_ids(db: Session, service_ids):
    ids = list(service_ids)
    services = db.query(Service).filter(Service.id.in_(ids)).all() if ids else []
    missing = set(ids) - {service.id for service in services}
    if missing:
        raise BusinessRuleViolation(f"Services do not exist: {sorted(missing)}")
    return services


def check_sufficient_duration(duration_minutes, service_ids, db: Session):
    total = sum(service.durationMinutes for service in services_by_ids(db, service_ids))
    if duration_minutes < total:
        raise BusinessRuleViolation("The appointment must cover the total duration of its services.")


def check_worker_service_compatibility(worker_id, service_ids, db: Session):
    allowed = set(get_worker_service_ids(db, worker_id))
    if not set(service_ids).issubset(allowed):
        raise BusinessRuleViolation("The worker must be qualified for every selected service.")


def check_package_discount(price, service_ids, db: Session):
    total = sum(service.price for service in services_by_ids(db, service_ids))
    if price >= total:
        raise BusinessRuleViolation("The package price must be lower than the total price of its services.")
