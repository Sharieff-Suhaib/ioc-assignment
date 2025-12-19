import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    model="google/flan-t5-small",
    token=os.getenv("LLM_API_KEY")
)

response = client.text_generation(
    "Say hello in one word",
    max_new_tokens=5
)

print(response)
