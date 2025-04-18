import os
from pydantic_ai import Agent
from app.services.tools import AVAILABLE_TOOLS

PRIMARY_MODEL = os.getenv("PRIMARY_LLM_MODEL", "agentica-org/deepcoder-14b-preview:free")
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

def run_autocoder_task(user_input: str):
    """Runs the autocoder task using LLMs with fallback."""
    response = None
    try:
        print(f"Attempting Autocoder Task with primary model: {PRIMARY_MODEL}")
        primary_agent = Agent(PRIMARY_MODEL, tools=AVAILABLE_TOOLS)
        response = primary_agent.run(f"Autocode task: {user_input}")
    except Exception as e:
        print(f"Primary model ({PRIMARY_MODEL}) failed for Autocoder Task: {e}")
        print(f"Attempting Autocoder Task with fallback model: {FALLBACK_MODEL}")
        try:
            fallback_agent = Agent(FALLBACK_MODEL, tools=AVAILABLE_TOOLS)
            response = fallback_agent.run(f"Autocode task: {user_input}")
        except Exception as fallback_e:
            print(f"Fallback model ({FALLBACK_MODEL}) also failed for Autocoder Task: {fallback_e}")
            response = f"Error: Autocoder task failed. Primary error: {e}. Fallback error: {fallback_e}"
    return response
