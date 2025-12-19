from typing import Dict, Any, List
from datetime import datetime
import re

class FunctionValidator:
    """Validates function inputs before execution"""
    
    MEDICAL_KEYWORDS = [
        "diagnose", "diagnosis", "treatment", "prescribe", "prescription",
        "cure", "disease", "symptom", "medication", "drug", "therapy"
    ]
    
    @staticmethod
    def validate_search_patient(args: Dict[str, Any]) -> tuple[bool, str]:
        """Validate search_patient arguments"""
        name = args.get("name")
        patient_id = args.get("patient_id")
        
        if not name and not patient_id:
            return False, "Either 'name' or 'patient_id' must be provided"
        
        if patient_id and not re.match(r'^P\d{3,}$', patient_id):
            return False, "Invalid patient_id format.  Expected format: P001"
        
        return True, "Valid"
    
    @staticmethod
    def validate_check_insurance(args: Dict[str, Any]) -> tuple[bool, str]: 
        """Validate insurance eligibility check"""
        patient_id = args.get("patient_id")
        
        if not patient_id:
            return False, "patient_id is required"
        
        if not re.match(r'^P\d{3,}$', patient_id):
            return False, "Invalid patient_id format"
        
        return True, "Valid"
    
    @staticmethod
    def validate_find_slots(args: Dict[str, Any]) -> tuple[bool, str]: 
        """Validate find_available_slots arguments"""
        specialty = args.get("specialty")
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        
        if not specialty:
            return False, "specialty is required"
        
        if not start_date or not end_date:
            return False, "Both start_date and end_date are required"
        
        # Validate date format
        try: 
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start > end: 
                return False, "start_date must be before end_date"
            
            if start < datetime.now():
                return False, "Cannot book appointments in the past"
                
        except ValueError:
            return False, "Dates must be in YYYY-MM-DD format"
        
        return True, "Valid"
    
    @staticmethod
    def validate_book_appointment(args: Dict[str, Any]) -> tuple[bool, str]:
        """Validate book_appointment arguments"""
        patient_id = args.get("patient_id")
        slot_id = args.get("slot_id")
        
        if not patient_id: 
            return False, "patient_id is required"
        
        if not slot_id:
            return False, "slot_id is required"
        
        return True, "Valid"
    
    @staticmethod
    def check_safety(user_input: str) -> tuple[bool, str]:
        """Check if request contains medical advice keywords"""
        input_lower = user_input.lower()
        
        for keyword in FunctionValidator.MEDICAL_KEYWORDS:
            if keyword in input_lower:
                return False, (
                    f"Request contains medical keyword '{keyword}'. "
                    "This agent cannot provide medical advice, diagnosis, or treatment recommendations.  "
                    "It can only coordinate appointments and administrative tasks."
                )
        
        return True, "Safe"

validator = FunctionValidator()