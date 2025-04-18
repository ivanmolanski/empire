from google.adk.agents import LlmAgent

ScraperAgent = LlmAgent(
    name="ScraperAgent",
    model="gemini-2.0-flash",
    description="Scrapes and extracts data from websites automatically."
)
