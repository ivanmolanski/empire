from google.adk.agents import LlmAgent

# LLM Agent for switching providers (OpenRouter, Gemini)
llm_switch_agent = LlmAgent(
    name="LLMSwitchAgent",
    model="gemini-2.0-flash",  # You can parameterize this
    description="Handles switching between LLM providers (OpenRouter, Gemini)."
)
