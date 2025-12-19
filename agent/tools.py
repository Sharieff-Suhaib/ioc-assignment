from pydantic import BaseModel, Field, validator
from typing import Optional
from api.mock_healthcare_api import healthcare_api
from agent.validators import validator as input_validator
from utils.audit_logger import audit_logger
from utils.config import config
import uuid


def search_patient_func(name: Optional[str] = None, patient_id: Optional[str] = None) -> dict:
    """Search for a patient by name or ID"""
    request_id = str(uuid.uuid4())[:8]
    
    args = {"name": name, "patient_id": patient_id}
    
    is_valid, message = input_validator. validate_search_patient(args)
    if not is_valid:  
        audit_logger.log_error(f"Validation failed: {message}", request_id)
        return {"error": message}
    
    audit_logger.log_function_call("search_patient", args, request_id, config.DRY_RUN_MODE)
    
    if config.DRY_RUN_MODE:
        return {"dry_run": True, "message": "Would search for patient", "args": args}
    
    try:
        result = healthcare_api.search_patient(name=name, patient_id=patient_id)
        
        if result:
            result_dict = result. model_dump()
            audit_logger.log_function_result("search_patient", result_dict, request_id)
            return result_dict
        else: 
            return {"error": "Patient not found"}
            
    except Exception as e:
        audit_logger.log_error(str(e), request_id)
        return {"error": str(e)}

def check_insurance_func(patient_id: str) -> dict:
    """Check insurance eligibility for a patient"""
    request_id = str(uuid.uuid4())[:8]
    
    args = {"patient_id":  patient_id}
    
    is_valid, message = input_validator.validate_check_insurance(args)
    if not is_valid: 
        audit_logger. log_error(f"Validation failed: {message}", request_id)
        return {"error": message}
    
    audit_logger.log_function_call("check_insurance_eligibility", args, request_id, config.DRY_RUN_MODE)
    
    if config.DRY_RUN_MODE:
        return {"dry_run": True, "message":  "Would check insurance eligibility", "args": args}
    
    try:
        result = healthcare_api.check_insurance_eligibility(patient_id)
        result_dict = result.model_dump()
        audit_logger.log_function_result("check_insurance_eligibility", result_dict, request_id)
        return result_dict
    except Exception as e:
        audit_logger.log_error(str(e), request_id)
        return {"error": str(e)}

def find_slots_func(specialty: str, start_date: str, end_date: str, provider:  Optional[str] = None) -> dict:
    """Find available appointment slots"""
    request_id = str(uuid.uuid4())[:8]
    
    args = {"specialty": specialty, "start_date":  start_date, "end_date": end_date, "provider":  provider}
    
    is_valid, message = input_validator.validate_find_slots(args)
    if not is_valid: 
        audit_logger. log_error(f"Validation failed: {message}", request_id)
        return {"error": message}
    
    audit_logger.log_function_call("find_available_slots", args, request_id, config.DRY_RUN_MODE)
    
    if config.DRY_RUN_MODE:
        return {"dry_run": True, "message": "Would find available slots", "args": args}
    
    try:
        result = healthcare_api.find_available_slots(specialty, start_date, end_date, provider)
        result_dict = {"slots": [slot.model_dump() for slot in result]}
        audit_logger. log_function_result("find_available_slots", result_dict, request_id)
        return result_dict
    except Exception as e:
        audit_logger.log_error(str(e), request_id)
        return {"error": str(e)}

def book_appointment_func(patient_id: str, slot_id: str, reason: str = "Follow-up consultation") -> dict:
    """Book an appointment for a patient"""
    request_id = str(uuid.uuid4())[:8]
    
    args = {"patient_id": patient_id, "slot_id": slot_id, "reason": reason}
    
    is_valid, message = input_validator.validate_book_appointment(args)
    if not is_valid: 
        audit_logger.log_error(f"Validation failed:  {message}", request_id)
        return {"error": message}
    
    audit_logger.log_function_call("book_appointment", args, request_id, config.DRY_RUN_MODE)
    
    if config.DRY_RUN_MODE:
        return {"dry_run": True, "message": "Would book appointment", "args": args}
    
    try: 
        result = healthcare_api.book_appointment(patient_id, slot_id, reason)
        result_dict = result.model_dump()
        audit_logger.log_function_result("book_appointment", result_dict, request_id)
        return result_dict
    except Exception as e:
        audit_logger.log_error(str(e), request_id)
        return {"error": str(e)}

# Export all tools
healthcare_tools = [
    search_patient_func,
    check_insurance_func,
    find_slots_func,
    book_appointment_func
]