# backend_v2/app/utils/sanitizers.py
import re

# List of forbidden phrases, normalized
FORBIDDEN_PHRASES = [
    "give me the code",
    "give me the solution",
    "write the code for me",
    "full solution",
    "full code",
    "just give me the answer",
    "provide the complete code",
    "what is the exact answer"
]

def is_prompt_forbidden(prompt: str) -> bool:
    """
    Checks if a prompt contains forbidden phrases.
    Normalizes text by lowercasing and removing punctuation.
    """
    normalized_prompt = re.sub(r'[^\w\s]', '', prompt.lower().strip())
    
    for phrase in FORBIDDEN_PHRASES:
        if phrase in normalized_prompt:
            return True
    return False

