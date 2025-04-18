from pydantic_ai import Agent
from pydantic import BaseModel, Field

# Example tool definition (replace/add your real tools here)
class GetWeatherParameters(BaseModel):
    location: str = Field(description="The city and state, e.g. San Francisco, CA")

@Agent.tool
def get_current_weather(parameters: GetWeatherParameters) -> str:
    """Get the current weather in a given location"""
    # ... implementation ...
    return '{"temperature": "72", "unit": "fahrenheit", "description": "sunny"}'

# Add your other tool definitions here using @Agent.tool

AVAILABLE_TOOLS = [get_current_weather]
