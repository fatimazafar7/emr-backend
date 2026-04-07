# Import all models to ensure relationships are properly established
from .user import User, UserRole
from .clinic import Clinic
from .doctor import Doctor
from .diagnosis import Diagnosis
from .visit import Visit
from .patient import Patient
from .appointment import Appointment
from .medical_record import MedicalRecord
from .prescription import Prescription
from .lab_result import LabResult
from .vital import Vital
from .billing import Billing
from .inventory import InventoryItem
from .ai_session import AISession

__all__ = [
    "User", "UserRole",
    "Clinic", 
    "Doctor",
    "Patient",
    "Appointment",
    "MedicalRecord",
    "Prescription", 
    "LabResult",
    "Vital",
    "Billing",
    "InventoryItem",
    "AISession",
    "Diagnosis",
    "Visit"
]