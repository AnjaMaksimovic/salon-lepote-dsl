"""Generated from model/salon_model.py; update the model or template before regenerating."""
from generated.dto import ClientDTO, PackageDTO, WorkerDTO, AppointmentDTO, ServiceDTO
from generated.schema import ClientOut, PackageOut, WorkerOut, AppointmentOut, ServiceOut

def client_to_dto(obj) -> ClientDTO:
    """SQLAlchemy Client entity -> ClientDTO (without ORM dependencies)."""
    return ClientDTO(
        id=obj.id,
        email=obj.email,
        name=obj.name,
        phone=obj.phone,
    )


def client_dto_to_out(dto: ClientDTO) -> ClientOut:
    """ClientDTO -> ClientOut (Pydantic API response schema)."""
    return ClientOut(**dto.__dict__)


def client_to_out(obj) -> ClientOut:
    """SQLAlchemy Client entity -> ClientOut, via a DTO."""
    return client_dto_to_out(client_to_dto(obj))

def package_to_dto(obj) -> PackageDTO:
    """SQLAlchemy Package entity -> PackageDTO (without ORM dependencies)."""
    return PackageDTO(
        id=obj.id,
        price=obj.price,
        name=obj.name,
    )


def package_dto_to_out(dto: PackageDTO) -> PackageOut:
    """PackageDTO -> PackageOut (Pydantic API response schema)."""
    return PackageOut(**dto.__dict__)


def package_to_out(obj) -> PackageOut:
    """SQLAlchemy Package entity -> PackageOut, via a DTO."""
    return package_dto_to_out(package_to_dto(obj))

def worker_to_dto(obj) -> WorkerDTO:
    """SQLAlchemy Worker entity -> WorkerDTO (without ORM dependencies)."""
    return WorkerDTO(
        id=obj.id,
        name=obj.name,
        surname=obj.surname,
        workingHoursTo=obj.workingHoursTo,
        workingHoursFrom=obj.workingHoursFrom,
    )


def worker_dto_to_out(dto: WorkerDTO) -> WorkerOut:
    """WorkerDTO -> WorkerOut (Pydantic API response schema)."""
    return WorkerOut(**dto.__dict__)


def worker_to_out(obj) -> WorkerOut:
    """SQLAlchemy Worker entity -> WorkerOut, via a DTO."""
    return worker_dto_to_out(worker_to_dto(obj))

def appointment_to_dto(obj) -> AppointmentDTO:
    """SQLAlchemy Appointment entity -> AppointmentDTO (without ORM dependencies)."""
    return AppointmentDTO(
        id=obj.id,
        dateTime=obj.dateTime,
        status=obj.status,
        durationMinutes=obj.durationMinutes,
        client_id=obj.client_id,
        worker_id=obj.worker_id,
    )


def appointment_dto_to_out(dto: AppointmentDTO) -> AppointmentOut:
    """AppointmentDTO -> AppointmentOut (Pydantic API response schema)."""
    return AppointmentOut(**dto.__dict__)


def appointment_to_out(obj) -> AppointmentOut:
    """SQLAlchemy Appointment entity -> AppointmentOut, via a DTO."""
    return appointment_dto_to_out(appointment_to_dto(obj))

def service_to_dto(obj) -> ServiceDTO:
    """SQLAlchemy Service entity -> ServiceDTO (without ORM dependencies)."""
    return ServiceDTO(
        id=obj.id,
        price=obj.price,
        category=obj.category,
        name=obj.name,
        durationMinutes=obj.durationMinutes,
    )


def service_dto_to_out(dto: ServiceDTO) -> ServiceOut:
    """ServiceDTO -> ServiceOut (Pydantic API response schema)."""
    return ServiceOut(**dto.__dict__)


def service_to_out(obj) -> ServiceOut:
    """SQLAlchemy Service entity -> ServiceOut, via a DTO."""
    return service_dto_to_out(service_to_dto(obj))
