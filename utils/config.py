import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    DRY_RUN_MODE = os.getenv("DRY_RUN_MODE", "false").lower() == "true"
    LOG_LEVEL = os. getenv("LOG_LEVEL", "INFO")
    MAX_FUNCTION_CALLS = int(os.getenv("MAX_FUNCTION_CALLS", "5"))
    HEALTHCARE_API_URL = os. getenv("HEALTHCARE_API_URL", "http://localhost:8000")
    
    @classmethod
    def validate(cls):
        if not cls.HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY not set in environment")
        return True

config = Config()