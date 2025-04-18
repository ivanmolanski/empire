from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

class ErrorHandlerAgent(BaseAgent):
    """Agent that monitors for errors and escalates or retries as needed."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        errors = ctx.session.state.get("errors", [])
        if errors:
            yield Event(author=self.name, content=f"Errors detected: {errors}", actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name, content="No errors detected.")
