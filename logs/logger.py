import json
from datetime import datetime

def log_action(data: dict):
    with open("logs/audit.log", "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }) + "\n")
