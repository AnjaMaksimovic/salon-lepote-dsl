"""Appointment availability and revenue reporting."""
from datetime import timedelta
from generated.entities import Appointment, Worker
from generated.enums import AppointmentStatus


def calculate_price(appointment, package=None):
    return package.price if package is not None else sum(service.price for service in appointment.service)


def has_no_overlap(db, worker_id, date_time, duration_minutes, excluded_appointment_id=None):
    end = date_time + timedelta(minutes=duration_minutes)
    appointments = db.query(Appointment).filter(Appointment.worker_id == worker_id).all()
    for appointment in appointments:
        if appointment.id == excluded_appointment_id or appointment.status == AppointmentStatus.CANCELLED:
            continue
        existing_end = appointment.dateTime + timedelta(minutes=appointment.durationMinutes)
        if date_time < existing_end and appointment.dateTime < end:
            return False
    return True


def suggest_alternative(db, requested_worker_id, service_ids, date_time, duration_minutes):
    workers = db.query(Worker).order_by(Worker.id).all()
    workers.sort(key=lambda worker: worker.id != requested_worker_id)
    required = set(service_ids)
    for worker in workers:
        if required.issubset({service.id for service in worker.service}) and has_no_overlap(
            db, worker.id, date_time, duration_minutes
        ):
            return {"available": True, "worker_id": worker.id}
    return {"available": False, "worker_id": None}


def revenue_report(db, date_from, date_to):
    appointments = db.query(Appointment).filter(
        Appointment.dateTime >= date_from, Appointment.dateTime <= date_to,
        Appointment.status == AppointmentStatus.COMPLETED,
    ).all()
    return {"appointment_count": len(appointments), "total_revenue": sum(calculate_price(t) for t in appointments)}
