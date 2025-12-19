from langchain.tools import tool
from services.insurance_service import check_insurance

@tool
def check_insurance_tool(patient_id: str, service_type: str):
    """Check insurance eligibility"""
    return check_insurance(patient_id, service_type)
