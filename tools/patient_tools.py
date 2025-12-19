from langchain.tools import tool
from services.patient_service import search_patient

@tool
def search_patient_tool(full_name: str):
    """Search patient by name"""
    return search_patient(full_name)
