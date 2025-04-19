from google.adk.agents import LlmAgent
import os

# LLM Agent for switching providers (OpenRouter, Gemini)
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

llm_switch_agent = LlmAgent(
    name="LLMSwitchAgent",
    model=FALLBACK_MODEL,  # Using environment variable for model name
    description="Handles switching between LLM providers (OpenRouter, Gemini)."
)
