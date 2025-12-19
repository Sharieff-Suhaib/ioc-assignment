from langchain_huggingface import HuggingFaceEndpoint
from agent.tools import search_patient_func, check_insurance_func, find_slots_func, book_appointment_func
from agent.validators import validator
from utils.audit_logger import audit_logger
from utils.config import config
import uuid
import json
import re
from datetime import datetime, timedelta

class ClinicalAgent:
    """Function-calling LLM agent for clinical workflow automation"""
    
    def __init__(self):
        config.validate()
        
        # Initialize HuggingFace LLM (optional - we'll use rule-based for demo)
        try:
            self.llm = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=config. HUGGINGFACE_API_KEY,
                max_new_tokens=512,
                temperature=0.1,
                top_k=10,
            )
            self.llm_available = True
        except Exception as e:
            print(f"⚠️  Warning: LLM not available ({e}). Using rule-based workflow only.")
            self.llm_available = False
    
    def execute_workflow(self, user_input:  str) -> list:
        """Execute workflow by calling functions in sequence"""
        results = []
        input_lower = user_input.lower()
        
        # Step 1: Extract and search for patient
        patient_name = None
        patient_id = None
        
        # Check for patient names
        if "ravi kumar" in input_lower: 
            patient_name = "Ravi Kumar"
        elif "priya sharma" in input_lower:
            patient_name = "Priya Sharma"
        
        # Check for patient ID (format: P001, P002, etc.)
        patient_id_match = re.search(r'P\d{3,}', user_input, re.IGNORECASE)
        if patient_id_match: 
            patient_id = patient_id_match.group().upper()
        
        # Search for patient
        if patient_name or patient_id:
            result = search_patient_func(name=patient_name, patient_id=patient_id)
            results.append({"function": "search_patient", "result": result})
            
            if "id" in result:
                patient_id = result["id"]
        
        # Step 2: Check insurance eligibility
        if patient_id and ("insurance" in input_lower or "eligibility" in input_lower or "coverage" in input_lower):
            result = check_insurance_func(patient_id)
            results.append({"function": "check_insurance_eligibility", "result": result})
        
        # Step 3: Find available slots
        specialty = None
        if "cardio" in input_lower:
            specialty = "cardiology"
        elif "ortho" in input_lower: 
            specialty = "orthopedics"
        elif "general" in input_lower:
            specialty = "general"
        elif "derma" in input_lower:
            specialty = "dermatology"
        
        if specialty and ("appointment" in input_lower or "slot" in input_lower or "schedule" in input_lower or "book" in input_lower):
            # Determine date range
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            if "next week" in input_lower: 
                start_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            elif "next month" in input_lower:
                start_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
            else:
                end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            
            result = find_slots_func(specialty, start_date, end_date)
            results.append({"function": "find_available_slots", "result": result})
            
            # Step 4: Book appointment if we have both patient and slots
            if patient_id and result. get("slots") and len(result["slots"]) > 0:
                slot_id = result["slots"][0]["slot_id"]
                reason = f"{specialty. title()} follow-up consultation"
                
                booking = book_appointment_func(patient_id, slot_id, reason)
                results.append({"function": "book_appointment", "result": booking})
        
        return results
    
    def process_request(self, user_input: str) -> dict:
        """Process a clinical workflow request"""
        request_id = str(uuid.uuid4())[:8]
        
        # Log request
        audit_logger.log_request(user_input, request_id)
        
        # Safety check
        is_safe, safety_message = validator. check_safety(user_input)
        if not is_safe: 
            audit_logger.log_refusal(safety_message, request_id)
            return {
                "status": "refused",
                "reason": safety_message,
                "request_id": request_id
            }
        
        try:
            # Execute workflow
            results = self.execute_workflow(user_input)
            
            if not results:
                return {
                    "status": "error",
                    "error": "Could not understand request.  Please specify:\n  - Patient name (Ravi Kumar, Priya Sharma) or ID (P001)\n  - Desired action (check insurance, schedule appointment)\n  - Specialty (cardiology, orthopedics)",
                    "request_id":  request_id
                }
            
            return {
                "status": "success",
                "workflow_results": results,
                "summary": self. generate_summary(results),
                "request_id": request_id
            }
            
        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            audit_logger.log_error(error_msg, request_id)
            return {
                "status": "error",
                "error": error_msg,
                "request_id": request_id
            }
    
    def generate_summary(self, results: list) -> str:
        """Generate human-readable summary"""
        summary = []
        
        for step in results:
            func_name = step["function"]
            result = step["result"]
            
            if "error" in result:
                summary. append(f"❌ {func_name}:  {result['error']}")
                continue
            
            if func_name == "search_patient": 
                if "name" in result:
                    summary.append(f"✓ Found patient: {result['name']} (ID: {result['id']})")
                    summary.append(f"  DOB: {result['date_of_birth']}, Phone: {result['phone']}")
            
            elif func_name == "check_insurance_eligibility":
                status = result.get("status", "unknown")
                summary.append(f"✓ Insurance status: {status. upper()}")
                if status == "active":
                    summary.append(f"  Coverage: {result.get('coverage_start')} to {result.get('coverage_end')}")
                    summary.append(f"  Co-pay: ₹{result.get('copay_amount', 0)}")
            
            elif func_name == "find_available_slots":
                slots = result.get("slots", [])
                summary.append(f"✓ Found {len(slots)} available slot(s)")
                if slots:
                    first_slot = slots[0]
                    summary.append(f"  Next available: {first_slot['start_time']} with {first_slot['provider']}")
            
            elif func_name == "book_appointment": 
                if "appointment_id" in result:
                    summary.append(f"✓ Appointment booked successfully!")
                    summary.append(f"  Appointment ID: {result['appointment_id']}")
                    summary.append(f"  Patient: {result['patient_name']}")
                    summary.append(f"  Provider: {result['provider']} ({result['specialty']})")
                    summary.append(f"  Time: {result['start_time']}")
                    summary.append(f"  Location: {result['location']}")
        
        return "\n".join(summary) if summary else "No actions completed"

def create_agent():
    """Factory function to create agent instance"""
    return ClinicalAgent()