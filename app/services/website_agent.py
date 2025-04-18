import os
from pydantic_ai import Agent
from app.services.tools import AVAILABLE_TOOLS

PRIMARY_MODEL = os.getenv("PRIMARY_LLM_MODEL", "agentica-org/deepcoder-14b-preview:free")
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

def run_website_management_task(user_input: str):
    """Runs the website management task using LLMs with fallback."""
    response = None
    try:
        print(f"Attempting Website Management with primary model: {PRIMARY_MODEL}")
        primary_agent = Agent(PRIMARY_MODEL, tools=AVAILABLE_TOOLS)
        response = primary_agent.run(f"Manage website task: {user_input}")
    except Exception as e:
        print(f"Primary model ({PRIMARY_MODEL}) failed for Website Management: {e}")
        print(f"Attempting Website Management with fallback model: {FALLBACK_MODEL}")
        try:
            fallback_agent = Agent(FALLBACK_MODEL, tools=AVAILABLE_TOOLS)
            response = fallback_agent.run(f"Manage website task: {user_input}")
        except Exception as fallback_e:
            print(f"Fallback model ({FALLBACK_MODEL}) also failed for Website Management: {fallback_e}")
            response = f"Error: Website management failed. Primary error: {e}. Fallback error: {fallback_e}"
    return response
