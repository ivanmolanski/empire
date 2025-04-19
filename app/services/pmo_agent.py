from google.adk.agents import BaseAgent, SequentialAgent, ParallelAgent, LoopAgent, LlmAgent
from google.adk.tools import agent_tool
from app.services.llm_agent import llm_switch_agent
from app.services.niche_agent import discovery_agent
from app.services.website_agent import website_agent
from app.services.analytics_agent import analytics_agent
from app.services.error_handler_agent import ErrorHandlerAgent
from app.services.review_agent import ReviewAgent
from app.services.autocoder_agent import AutoCoderAgent
from app.services.artifact_agent import ArtifactAgent
from app.services.memory_agent import MemoryAgent
from app.services.seo_agent import SEOAgent
from app.services.scraper_agent import ScraperAgent
from app.services.human_in_loop_agent import HumanInLoopAgent
from app.services.command_agent import CommandAgent
from typing import AsyncGenerator
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Example: Parallelize niche discovery and analytics, then sequence website creation
parallel_gather = ParallelAgent(
    name="ParallelGather",
    sub_agents=[discovery_agent, analytics_agent]
)

# Example: LoopAgent for iterative refinement (e.g., website optimization)
class WebsiteRefinementAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Example: Check if website meets criteria, else escalate
        status = ctx.session.state.get("website_status", "needs_improvement")
        should_stop = (status == "approved")
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

refinement_loop = LoopAgent(
    name="WebsiteRefinementLoop",
    max_iterations=5,
    sub_agents=[website_agent, WebsiteRefinementAgent(name="RefinementChecker")]
)

# Main workflow: gather info in parallel, then refine website
main_workflow = SequentialAgent(
    name="MainWorkflow",
    sub_agents=[llm_switch_agent, parallel_gather, refinement_loop]
)

# PMO/master agent with all sub-agents and tools
class PMOAgent(BaseAgent):
    sub_agents: list = []
    tools: list = []
    
    def __init__(self):
        super().__init__(name="PMOAgent", description="Master agent orchestrating all sub-agents and workflows.")
        self.sub_agents = [main_workflow]
        self.tools = [agent_tool.AgentTool(agent=website_agent)]
        for agent in self.sub_agents:
            agent.parent_agent = self

pmo_agent = PMOAgent()

# Memory/session setup
APP_NAME = "bach_ai_multiagent"
USER_ID = "user_test_1"  # You can parameterize this per user
SESSION_ID = "session_001"  # You can generate or parameterize this per chat

# 1. Create the Session Service instance (in-memory for dev)
session_service = InMemorySessionService()

# 2. Create the specific session (optionally initialize state)
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
    # state={"initial_key": "initial_value"}  # Optional
)

# 3. Create the Runner instance (orchestrates agent execution with memory)
runner = Runner(
    agent=pmo_agent,  # The root/master agent
    app_name=APP_NAME,
    session_service=session_service
)

# Example: To run the agent with memory, use runner.run() or runner.run_async()
# You can now access session.state for persistent memory across turns.

# --- Agent Validator (final step in workflow) ---
class AgentValidator(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Example: Check if all required state keys are present and valid
        errors = []
        if ctx.session.state.get("website_status") != "approved":
            errors.append("Website not approved.")
        if ctx.session.state.get("niche_found") is not True:
            errors.append("Niche discovery incomplete.")
        if errors:
            yield Event(author=self.name, content="; ".join(errors), actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name, content="All agents completed successfully.")

# Add validator as the last step in the main workflow
main_workflow.sub_agents.append(AgentValidator(name="AgentValidator"))

# Instantiate specialized agents
error_handler_agent = ErrorHandlerAgent(name="ErrorHandlerAgent", description="Handles error monitoring and escalation.")
review_agent = ReviewAgent(name="ReviewAgent", description="Reviews outputs from other agents.")
autocoder_agent = AutoCoderAgent
artifact_agent = ArtifactAgent(name="ArtifactAgent", description="Manages artifacts.")
memory_agent = MemoryAgent(name="MemoryAgent", description="Handles advanced memory/search.")
seo_agent = SEOAgent
scraper_agent = ScraperAgent
human_in_loop_agent = HumanInLoopAgent(name="HumanInLoopAgent", description="Escalates to human when needed.")

# Add all specialized agents to the main workflow for full automation
main_workflow.sub_agents.extend([
    error_handler_agent,
    review_agent,
    autocoder_agent,
    artifact_agent,
    memory_agent,
    seo_agent,
    scraper_agent,
    human_in_loop_agent
])

# Instantiate CommandAgent with all available agents
all_agents = [
    llm_switch_agent, discovery_agent, website_agent, analytics_agent,
    error_handler_agent, review_agent, autocoder_agent, artifact_agent,
    memory_agent, seo_agent, scraper_agent, human_in_loop_agent
]
command_agent = CommandAgent(available_agents=all_agents)

# Add CommandAgent as a sub-agent for chat-based help and discoverability
main_workflow.sub_agents.insert(0, command_agent)
