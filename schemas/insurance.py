from pydantic import BaseModel

class InsuranceEligibilityRequest(BaseModel):
    patient_id: str
    service_type: str

class InsuranceEligibilityResponse(BaseModel):
    eligible: bool
    payer: str
    copay: int | None
