import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class AuditLogger:
    """HIPAA-compliant audit logging for all agent actions"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        log_file = self. log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ClinicalAgent")
    
    def log_request(self, user_input: str, request_id: str):
        """Log incoming user request"""
        self.logger.info(f"[REQUEST:{request_id}] User Input: {user_input}")
    
    def log_function_call(self, function_name: str, arguments: Dict[str, Any], request_id: str, dry_run: bool = False):
        """Log function call with full parameters"""
        mode = "DRY_RUN" if dry_run else "EXECUTE"
        self.logger.info(
            f"[{mode}:{request_id}] Function: {function_name} | Args: {json.dumps(arguments)}"
        )
    
    def log_function_result(self, function_name: str, result: Any, request_id: str):
        """Log function execution result"""
        self.logger. info(
            f"[RESULT:{request_id}] Function: {function_name} | Result: {json.dumps(result, default=str)}"
        )
    
    def log_refusal(self, reason: str, request_id: str):
        """Log when agent refuses to act"""
        self.logger.warning(f"[REFUSAL:{request_id}] Reason: {reason}")
    
    def log_error(self, error:  str, request_id: str):
        """Log errors"""
        self.logger.error(f"[ERROR:{request_id}] {error}")

audit_logger = AuditLogger()