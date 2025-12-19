from fastapi import FastAPI
from agent.orchestrator import run_agent
from utils.logger import log_action

app = FastAPI()

@app.post("/run")
def run(request: dict):
    result = run_agent(request["text"])
    log_action({"input": request["text"], "output": result})
    return result
