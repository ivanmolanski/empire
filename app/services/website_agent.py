from pydantic_ai import Agent
from app.services.tools import AVAILABLE_TOOLS
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def run_website_management_task(user_input: str):
    """Runs the website management task using LLMs with fallback."""
    response = None
    try:
        logger.info(f"Attempting Website Management with primary model: {settings.PRIMARY_LLM_MODEL}")
        primary_agent = Agent(settings.PRIMARY_LLM_MODEL, tools=AVAILABLE_TOOLS)
        response = primary_agent.run(f"Manage website task: {user_input}")
    except Exception as e:
        logger.error(f"Primary model ({settings.PRIMARY_LLM_MODEL}) failed for Website Management: {str(e)}")
        logger.info(f"Attempting Website Management with fallback model: {settings.FALLBACK_LLM_MODEL}")
        try:
            fallback_agent = Agent(settings.FALLBACK_LLM_MODEL, tools=AVAILABLE_TOOLS)
            response = fallback_agent.run(f"Manage website task: {user_input}")
        except Exception as fallback_e:
            logger.error(f"Fallback model ({settings.FALLBACK_LLM_MODEL}) also failed for Website Management: {str(fallback_e)}")
            # Add capability information to help diagnose issues
            response = {
                "error": True,
                "message": "Website management failed with both primary and fallback models",
                "details": {
                    "primary_error": str(e),
                    "fallback_error": str(fallback_e),
                    "primary_model": settings.PRIMARY_LLM_MODEL,
                    "fallback_model": settings.FALLBACK_LLM_MODEL
                }
            }
    return response
