from google.adk.agents import LlmAgent

SEOAgent = LlmAgent(
    name="SEOAgent",
    model="gemini-2.0-flash",
    description="Optimizes websites for SEO automatically."
)
