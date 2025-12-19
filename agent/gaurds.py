def validate_request(text: str):
    forbidden = ["diagnose", "medication", "treatment", "dose"]
    if any(word in text.lower() for word in forbidden):
        raise ValueError("Medical advice is not allowed")
