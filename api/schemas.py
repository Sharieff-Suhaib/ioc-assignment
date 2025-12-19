from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class InsuranceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    PENDING = "pending"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Patient(BaseModel):
    """FHIR-compliant Patient resource"""
    id: str
    name: str
    date_of_birth: str
    gender: str
    phone:  str
    email: Optional[str] = None
    insurance_id: Optional[str] = None
    
    @validator('date_of_birth')
    def validate_dob(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError: 
            raise ValueError("Date of birth must be in YYYY-MM-DD format")

class InsuranceEligibility(BaseModel):
    """Insurance eligibility check result"""
    patient_id: str
    insurance_id: str
    status: InsuranceStatus
    coverage_start: str
    coverage_end:  str
    copay_amount: float
    message: str

class TimeSlot(BaseModel):
    """Available appointment time slot"""
    slot_id: str
    provider:  str
    specialty: str
    start_time:  datetime
    end_time: datetime
    location: str

class Appointment(BaseModel):
    """FHIR-compliant Appointment resource"""
    appointment_id: str
    patient_id: str
    patient_name: str
    provider:  str
    specialty: str
    start_time: datetime
    end_time: datetime
    location: str
    status: AppointmentStatus
    reason: Optional[str] = None
    notes: Optional[str] = None