from pydantic import BaseModel

class PatientSearchRequest(BaseModel):
    full_name: str
    date_of_birth: str | None = None

class Patient(BaseModel):
    patient_id: str
    full_name: str
    dob: str | None = None
