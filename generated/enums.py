"""Generated from model/salon_model.py; update the model or template before regenerating."""
import enum


class ServiceCategory(enum.Enum):
    HAIR_REMOVAL = "HAIR_REMOVAL"
    HAIRCUT = "HAIRCUT"
    LASH_BROW = "LASH_BROW"
    MANICURE_PEDICURE = "MANICURE_PEDICURE"
    FACIAL_CARE = "FACIAL_CARE"

class AppointmentStatus(enum.Enum):
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SCHEDULED = "SCHEDULED"

