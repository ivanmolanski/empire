from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

class HumanInLoopAgent(BaseAgent):
    """Agent that escalates to a human or external system when needed."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Placeholder: Add logic to notify human or external system
        yield Event(author=self.name, content="Escalated to human for review.", actions=EventActions(escalate=True))
