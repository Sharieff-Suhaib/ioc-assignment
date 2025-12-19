from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools.patient_tools import search_patient_tool
from tools.insurance_tools import check_insurance_tool
from agent.gaurds import validate_request
from tools.appointment_tools import (
    find_available_slots_tool,
    book_appointment_tool
)

llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini"
)

agent = initialize_agent(
    tools=[
        search_patient_tool,
        check_insurance_tool,
        find_available_slots_tool,
        book_appointment_tool
    ],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

def run_agent(user_input: str):
    validate_request(user_input)
    return agent.run(user_input)
