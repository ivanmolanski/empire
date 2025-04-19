from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

class CommandAgent(BaseAgent):
    """Agent that lists available commands and helps the user via chat."""
    available_agents: list = []
    
    def __init__(self, available_agents):
        super().__init__(name="CommandAgent", description="Lists and helps with available agent commands.")
        self.available_agents = available_agents

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # List available agent commands
        commands = [f"{agent.name}: {agent.description}" for agent in self.available_agents]
        help_text = "Available commands:\n" + "\n".join(commands)
        yield Event(author=self.name, content=help_text)
