from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

class ReviewAgent(BaseAgent):
    """Agent that reviews outputs from other agents (generator-critic pattern)."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        output = ctx.session.state.get("last_output", "")
        # Placeholder: Add real review/critique logic here
        if "error" in output.lower():
            yield Event(author=self.name, content="Review: Output contains errors.")
        else:
            yield Event(author=self.name, content="Review: Output looks good.")
