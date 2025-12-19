from datetime import datetime, timedelta
from typing import Optional, List
from api.schemas import (
    Patient, InsuranceEligibility, InsuranceStatus, 
    TimeSlot, Appointment, AppointmentStatus
)
import random

class MockHealthcareAPI:
    """Simulated healthcare backend for demo purposes"""
    
    def __init__(self):
        self.patients = {
            "P001": Patient(
                id="P001",
                name="Ravi Kumar",
                date_of_birth="1985-03-15",
                gender="male",
                phone="+91-9876543210",
                email="ravi. kumar@email.com",
                insurance_id="INS-RK-2024"
            ),
            "P002": Patient(
                id="P002",
                name="Priya Sharma",
                date_of_birth="1990-07-22",
                gender="female",
                phone="+91-9876543211",
                email="priya.sharma@email.com",
                insurance_id="INS-PS-2024"
            ),
            "P003": Patient(
                id="P003",
                name="Amit Singh",
                date_of_birth="1978-11-05",
                gender="male",
                phone="+91-9876543212",
                email="amit.singh@email.com",
                insurance_id="INS-AS-2024"
            )
        }
        
        self.appointments = {}
        self.appointment_counter = 1000
    
    def search_patient(self, name: str = None, patient_id: str = None) -> Optional[Patient]:
        """Search for patient by name or ID"""
        if patient_id:
            return self.patients.get(patient_id)
        
        if name:
            for patient in self.patients.values():
                if name.lower() in patient.name.lower():
                    return patient
        
        return None
    
    def check_insurance_eligibility(self, patient_id: str) -> InsuranceEligibility:
        """Check insurance eligibility for patient"""
        patient = self.patients.get(patient_id)
        
        if not patient or not patient.insurance_id:
            return InsuranceEligibility(
                patient_id=patient_id,
                insurance_id="N/A",
                status=InsuranceStatus.INACTIVE,
                coverage_start="",
                coverage_end="",
                copay_amount=0.0,
                message="No insurance found for patient"
            )
        
        return InsuranceEligibility(
            patient_id=patient_id,
            insurance_id=patient.insurance_id,
            status=InsuranceStatus.ACTIVE,
            coverage_start="2024-01-01",
            coverage_end="2024-12-31",
            copay_amount=500.0,
            message="Patient is eligible for coverage"
        )
    
    def find_available_slots(
        self, 
        specialty: str, 
        start_date: str, 
        end_date:  str,
        provider: Optional[str] = None
    ) -> List[TimeSlot]: 
        """Find available appointment slots"""
        slots = []
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        providers = {
            "cardiology": ["Dr.  Mehta", "Dr. Patel"],
            "orthopedics": ["Dr. Singh", "Dr. Reddy"],
            "general": ["Dr. Kumar", "Dr. Gupta"]
        }
        
        specialty_lower = specialty.lower()
        available_providers = providers.get(specialty_lower, ["Dr. General"])
        
        if provider:
            available_providers = [provider] if provider in available_providers else available_providers
        
        current = start
        slot_id = 1
        
        while current <= end and len(slots) < 5:
            if current. weekday() < 5:  # Weekdays only
                for hour in [9, 11, 14, 16]: 
                    start_time = current.replace(hour=hour, minute=0, second=0)
                    end_time = start_time + timedelta(hours=1)
                    
                    slots.append(TimeSlot(
                        slot_id=f"SLOT-{slot_id: 04d}",
                        provider=random.choice(available_providers),
                        specialty=specialty,
                        start_time=start_time,
                        end_time=end_time,
                        location=f"{specialty.title()} Department, Main Hospital"
                    ))
                    slot_id += 1
            
            current += timedelta(days=1)
        
        return slots[: 5] 
    
    def book_appointment(
        self,
        patient_id: str,
        slot_id: str,
        reason: str = "Follow-up consultation"
    ) -> Appointment:
        """Book an appointment for a patient"""
        patient = self.patients.get(patient_id)
        
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        
        appointment_id = f"APT-{self.appointment_counter:06d}"
        self.appointment_counter += 1
        
        start_time = datetime.now() + timedelta(days=7)
        
        appointment = Appointment(
            appointment_id=appointment_id,
            patient_id=patient_id,
            patient_name=patient. name,
            provider="Dr. Mehta",
            specialty="Cardiology",
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            location="Cardiology Department, Main Hospital",
            status=AppointmentStatus.BOOKED,
            reason=reason,
            notes=f"Slot ID: {slot_id}"
        )
        
        self.appointments[appointment_id] = appointment
        return appointment

healthcare_api = MockHealthcareAPI()