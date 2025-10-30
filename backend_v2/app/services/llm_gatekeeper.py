# backend_v2/app/services/llm_gatekeeper.py
import asyncio
from app.utils.sanitizers import is_prompt_forbidden

async def get_llm_assistance(prompt: str) -> tuple[str, bool]:
    """
    Mock LLM assistance service.
    Checks for forbidden prompts and returns a mock response.
    
    In a real app, this would make an API call to an LLM.
    """
    if is_prompt_forbidden(prompt):
        return (
            "I cannot provide the full solution. Please rephrase your question to ask for a hint, clarification, or an explanation of a concept.",
            True
        )
    
    # Simulate an async API call to an LLM
    await asyncio.sleep(0.5) 
    
    # Mock response logic based on prompt
    if "how do i start" in prompt.lower():
        response = "Think about the data structure you need to use. What are the inputs and outputs?"
    elif "edge cases" in prompt.lower():
        response = "A good edge case to consider is an empty input. What should happen then?"
    else:
        response = "This is a helpful hint to guide you in the right direction. Consider the main logic loop."
    
    return (response, False)

