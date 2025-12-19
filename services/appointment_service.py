def find_slots(department: str, start: str, end: str):
    return [
        {
            "slot_id": "slot_101",
            "time": "2025-01-10T10:00"
        }
    ]

def book_appointment(patient_id: str, slot_id: str, dry_run: bool):
    if dry_run:
        return {"status": "DRY_RUN", "slot_id": slot_id}
    return {"status": "CONFIRMED", "appointment_id": "apt_999"}
