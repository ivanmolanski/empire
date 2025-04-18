import os
from pydantic_ai import Agent
from app.services.tools import AVAILABLE_TOOLS

PRIMARY_MODEL = os.getenv("PRIMARY_LLM_MODEL", "agentica-org/deepcoder-14b-preview:free")
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

def run_discovery_agent(user_input: str):
    try:
        agent = Agent(PRIMARY_MODEL, tools=AVAILABLE_TOOLS)
        return agent.run(user_input)
    except Exception as e:
        try:
            fallback_agent = Agent(FALLBACK_MODEL, tools=AVAILABLE_TOOLS)
            return fallback_agent.run(user_input)
        except Exception as fallback_e:
            return f"Error: Both models failed. Primary error: {e}. Fallback error: {fallback_e}"

# Example for website agent

def run_website_agent(user_input: str):
    try:
        agent = Agent(PRIMARY_MODEL, tools=AVAILABLE_TOOLS)
        return agent.run(user_input)
    except Exception as e:
        try:
            fallback_agent = Agent(FALLBACK_MODEL, tools=AVAILABLE_TOOLS)
            return fallback_agent.run(user_input)
        except Exception as fallback_e:
            return f"Error: Both models failed. Primary error: {e}. Fallback error: {fallback_e}"
