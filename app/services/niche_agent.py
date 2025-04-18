import os
from pydantic_ai import Agent
from app.services.tools import AVAILABLE_TOOLS

PRIMARY_MODEL = os.getenv("PRIMARY_LLM_MODEL", "agentica-org/deepcoder-14b-preview:free")
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

def run_niche_discovery_task(user_input: str):
    """Runs the niche discovery task using LLMs with fallback."""
    response = None
    try:
        print(f"Attempting Niche Discovery with primary model: {PRIMARY_MODEL}")
        primary_agent = Agent(PRIMARY_MODEL, tools=AVAILABLE_TOOLS)
        response = primary_agent.run(f"Analyze the market for niches based on: {user_input}")
    except Exception as e:
        print(f"Primary model ({PRIMARY_MODEL}) failed for Niche Discovery: {e}")
        print(f"Attempting Niche Discovery with fallback model: {FALLBACK_MODEL}")
        try:
            fallback_agent = Agent(FALLBACK_MODEL, tools=AVAILABLE_TOOLS)
            response = fallback_agent.run(f"Analyze the market for niches based on: {user_input}")
        except Exception as fallback_e:
            print(f"Fallback model ({FALLBACK_MODEL}) also failed for Niche Discovery: {fallback_e}")
            response = f"Error: Niche discovery failed. Primary error: {e}. Fallback error: {fallback_e}"
    return response
