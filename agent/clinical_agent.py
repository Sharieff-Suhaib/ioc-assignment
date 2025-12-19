from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core. prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agent.tools import search_patient_func, check_insurance_func, find_slots_func, book_appointment_func
from agent.validators import validator
from utils.audit_logger import audit_logger
from utils.config import config
import uuid
import json
from datetime import datetime, timedelta

class ClinicalAgent:
    """LLM-powered function-calling agent for clinical workflow automation"""
    
    # System prompt that teaches the LLM how to behave
    SYSTEM_PROMPT = """You are a clinical workflow coordinator AI. Your job is to help schedule appointments and perform administrative tasks. 

CRITICAL RULES:
1. You CANNOT provide medical advice, diagnosis, or treatment recommendations
2. You CAN ONLY coordinate appointments and check administrative information
3. You must respond ONLY in valid JSON format

Available functions:
- search_patient:  Find a patient by name or ID
  Args: {{"name": "patient name"}} OR {{"patient_id": "P001"}}
  
- check_insurance_eligibility: Check insurance coverage
  Args: {{"patient_id": "P001"}}
  
- find_available_slots:  Search for appointment slots
  Args: {{"specialty": "cardiology", "start_date": "2025-12-20", "end_date": "2025-12-27"}}
  
- book_appointment: Book an appointment
  Args: {{"patient_id": "P001", "slot_id": "SLOT-0001", "reason": "Follow-up"}}

Your response must be a JSON object with this structure:
{{
  "intent": "schedule_appointment" | "check_insurance" | "search_patient" | "refuse",
  "reasoning": "brief explanation of what you understood",
  "actions": [
    {{"function":  "function_name", "args": {{"param":  "value"}}}},
    ... 
  ]
}}

If the request is about medical advice (diagnosis, treatment, medication), respond:
{{
  "intent": "refuse",
  "reasoning": "This is a medical advice request which I cannot handle",
  "actions": []
}}

Examples: 

User: "Schedule a cardiology appointment for Ravi Kumar next week"
Response: 
{{
  "intent": "schedule_appointment",
  "reasoning": "User wants to book a cardiology appointment for patient Ravi Kumar in the next week",
  "actions": [
    {{"function": "search_patient", "args": {{"name": "Ravi Kumar"}}}},
    {{"function":  "find_available_slots", "args": {{"specialty": "cardiology", "start_date": "2025-12-26", "end_date": "2026-01-02"}}}},
    {{"function": "book_appointment", "args": {{"patient_id": "{{PATIENT_ID}}", "slot_id": "{{SLOT_ID}}", "reason": "Cardiology follow-up"}}}}
  ]
}}

User: "What medication should I take for headache?"
Response:
{{
  "intent": "refuse",
  "reasoning": "This is a medical advice request about medication",
  "actions": []
}}

Now process this request:
User: {user_input}

Response (JSON only):"""

    def __init__(self):
        config.validate()
        
        print("🔄 Initializing LLM...")
        
        llm_endpoint = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            task="conversational",
            huggingfacehub_api_token=config.API_KEY,
            max_new_tokens=1024,
            temperature=0.1,
        )

        self.llm = ChatHuggingFace(llm=llm_endpoint)
        
        self.prompt = ChatPromptTemplate. from_template(self.SYSTEM_PROMPT)
        
        self.json_parser = JsonOutputParser()
        
        self.function_map = {
            "search_patient": search_patient_func,
            "check_insurance_eligibility": check_insurance_func,
            "find_available_slots": find_slots_func,
            "book_appointment": book_appointment_func
        }
        
        print("✅ LLM initialized successfully!")
    
    def parse_llm_response(self, response) -> dict:
        """Extract JSON from LLM response"""
        try:
            import re
            
            if hasattr(response, 'content'):
                response_text = response.content  
            else:
                response_text = str(response)
            
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re. sub(r'```\s*', '', response_text)
            
            response_text = response_text.split('\n\nReplace')[0]  
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            return {
                "intent": "error",
                "reasoning": "Could not find JSON in response",
                "actions": []
            }
        except Exception as e:
            return {
                "intent": "error",
                "reasoning": f"JSON parsing error: {str(e)}",
                "actions": []
        }
    
    def execute_llm_workflow(self, user_input: str) -> list:
        """Use LLM to parse intent and execute workflow"""
        results = []
        
        print("\n🤖 LLM is analyzing your request...")
        
        prompt_text = self.prompt.format(user_input=user_input)
        llm_response = self.llm.invoke(prompt_text)
        
        print(f"📝 LLM Response:\n{llm_response}\n")
        
        parsed = self.parse_llm_response(llm_response)
        
        print(f"🧠 LLM Understanding:")
        print(f"   Intent: {parsed.get('intent')}")
        print(f"   Reasoning: {parsed.get('reasoning')}\n")
        
        if parsed.get('intent') == 'refuse':
            return [{
                "function": "refusal",
                "result": {"refused": True, "reason": parsed.get('reasoning')}
            }]
        
        if parsed.get('intent') == 'error':
            print("⚠️ LLM parsing failed, using rule-based fallback")
            return self. execute_rule_based_workflow(user_input)
        
        actions = parsed.get('actions', [])
        context = {}
        
        for i, action in enumerate(actions):
            function_name = action.get('function')
            args = action.get('args', {}).copy()
            
            print(f"⚙️ Executing function {i+1}/{len(actions)}: {function_name}")
            
            for key, value in list(args.items()):
                if isinstance(value, str):
                    if '{PATIENT_ID}' in value: 
                        if 'patient_id' in context:
                            args[key] = context['patient_id']
                            print(f"   🔄 Replaced {{{key. upper()}}} with {context['patient_id']}")
                        else: 
                            print(f"   ⚠️ Warning: {{{key.upper()}}} placeholder but no patient_id in context yet")
                    
                    if '{SLOT_ID}' in value:
                        if 'slot_id' in context:
                            args[key] = context['slot_id']
                            print(f"   🔄 Replaced {{SLOT_ID}} with {context['slot_id']}")
                        else:
                            print(f"   ⚠️ Warning: {{SLOT_ID}} placeholder but no slot_id in context yet")
            
            func = self.function_map.get(function_name)
            if not func:
                print(f"   ⚠️ Unknown function: {function_name}")
                continue
            
            try: 
                if 'start_date' in args and ('XX' in str(args.get('start_date', '')) or 'YY' in str(args.get('end_date', ''))):
                    start = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                    end = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
                    args['start_date'] = start
                    args['end_date'] = end
                
                result = func(**args)
                results.append({"function": function_name, "result":  result})
                
                if function_name == "search_patient" and "id" in result and not result. get("error"):
                    context['patient_id'] = result['id']
                    print(f"   💾 Stored patient_id = {context['patient_id']}")
                
                if function_name == "find_available_slots" and "slots" in result and result['slots']:
                    context['slot_id'] = result['slots'][0]['slot_id']
                    print(f"   💾 Stored slot_id = {context['slot_id']}")
                
                print(f"   ✅ Success: {function_name}")
                
            except Exception as e:
                print(f"   ❌ Error:  {str(e)}")
                results.append({"function": function_name, "result": {"error": str(e)}})
    
        return results
    
    def execute_rule_based_workflow(self, user_input: str) -> list:
        """Fallback:  Rule-based workflow (your current implementation)"""
        print("⚠️  Using rule-based fallback (LLM failed)")
        
        results = []
        input_lower = user_input.lower()
        
        patient_name = None
        patient_id = None
        
        if "ravi kumar" in input_lower:
            patient_name = "Ravi Kumar"
        elif "priya sharma" in input_lower:
            patient_name = "Priya Sharma"
        
        import re
        patient_id_match = re.search(r'P\d{3,}', user_input, re.IGNORECASE)
        if patient_id_match:
            patient_id = patient_id_match.group().upper()
        
        if patient_name or patient_id:
            result = search_patient_func(name=patient_name, patient_id=patient_id)
            results.append({"function": "search_patient", "result": result})
            if "id" in result:
                patient_id = result["id"]
        
        if patient_id and ("insurance" in input_lower or "eligibility" in input_lower):
            result = check_insurance_func(patient_id)
            results.append({"function": "check_insurance_eligibility", "result": result})
        
        specialty = None
        if "cardio" in input_lower:
            specialty = "cardiology"
        elif "ortho" in input_lower: 
            specialty = "orthopedics"
        
        if specialty and ("appointment" in input_lower or "schedule" in input_lower):
            start_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            
            result = find_slots_func(specialty, start_date, end_date)
            results.append({"function": "find_available_slots", "result": result})
            
            if patient_id and result. get("slots"):
                slot_id = result["slots"][0]["slot_id"]
                booking = book_appointment_func(patient_id, slot_id, f"{specialty} follow-up")
                results.append({"function": "book_appointment", "result": booking})
        
        return results
    
    def process_request(self, user_input: str) -> dict:
        """Process a clinical workflow request using LLM"""
        request_id = str(uuid.uuid4())[:8]
        
        audit_logger.log_request(user_input, request_id)
        
        is_safe, safety_message = validator.check_safety(user_input)
        if not is_safe: 
            audit_logger.log_refusal(safety_message, request_id)
            return {
                "status": "refused",
                "reason": safety_message,
                "request_id": request_id
            }
        
        try:
            try:
                results = self.execute_llm_workflow(user_input)
            except Exception as e:
                print(f"⚠️  LLM workflow failed: {e}")
                results = self.execute_rule_based_workflow(user_input)
            
            if results and results[0]. get("function") == "refusal":
                return {
                    "status":  "refused",
                    "reason": results[0]["result"]["reason"],
                    "request_id": request_id
                }
            
            if not results:
                return {
                    "status": "error",
                    "error": "Could not understand request. Please specify patient and desired action.",
                    "request_id": request_id
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
                "status":  "error",
                "error":  error_msg,
                "request_id": request_id
            }
    
    def generate_summary(self, results: list) -> str:
        """Generate human-readable summary"""
        summary = []
        
        for step in results:
            func_name = step["function"]
            result = step["result"]
            
            if "error" in result:
                summary.append(f"❌ {func_name}:  {result['error']}")
                continue
            
            if func_name == "search_patient": 
                if "name" in result:
                    summary.append(f"✓ Found patient: {result['name']} (ID: {result['id']})")
                    summary.append(f"  DOB: {result['date_of_birth']}, Phone: {result['phone']}")
            
            elif func_name == "check_insurance_eligibility":
                status = result.get("status", "unknown")
                summary.append(f"✓ Insurance status: {status. upper()}")
                if status == "active":
                    summary.append(f"  Coverage: {result. get('coverage_start')} to {result.get('coverage_end')}")
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
                    summary.append(f"  Patient:  {result['patient_name']}")
                    summary.append(f"  Provider: {result['provider']} ({result['specialty']})")
                    summary.append(f"  Time: {result['start_time']}")
                    summary.append(f"  Location: {result['location']}")
        
        return "\n".join(summary) if summary else "No actions completed"

def create_agent():
    """Factory function to create agent instance"""
    return ClinicalAgent()