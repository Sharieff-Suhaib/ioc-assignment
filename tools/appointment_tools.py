from langchain.tools import tool
from services.appointment_service import find_slots, book_appointment
import os

@tool
def find_available_slots_tool(department: str, start: str, end: str):
    return find_slots(department, start, end)

@tool
def book_appointment_tool(patient_id: str, slot_id: str):
    dry_run = os.getenv("DRY_RUN") == "true"
    return book_appointment(patient_id, slot_id, dry_run)
