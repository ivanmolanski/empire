"""
Central initialization module for the Empire multi-agent orchestration framework.
This module provides a single entry point for accessing the core components.
"""
import logging
from app.core.agent import Agent
from app.core.communication import MessageBus
from app.core.memory import MemoryManager
from app.core.role_negotiation import RoleManager
from app.core.orchestrator import Orchestrator
from app.core.tools import ToolExecutor

logger = logging.getLogger(__name__)

class Empire:
    """
    Main entry point for the Empire multi-agent orchestration framework.
    Provides access to all core components and manages initialization.
    """
    
    def __init__(self):
        """Initialize the Empire framework."""
        self.message_bus = MessageBus()
        self.memory_manager = MemoryManager()
        self.role_manager = RoleManager()
        self.orchestrator = Orchestrator(self.message_bus, self.role_manager)
        self._agents = {}  # agent_id -> Agent
        
        logger.info("Empire multi-agent orchestration framework initialized")
    
    def register_agent(self, agent: Agent) -> str:
        """
        Register an agent with the framework.
        Returns the agent's ID.
        """
        self._agents[agent.agent_id] = agent
        self.orchestrator.register_agent(agent)
        logger.info(f"Agent '{agent.name}' (ID: {agent.agent_id}) registered with Empire")
        return agent.agent_id
    
    def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
    
    def list_agents(self):
        """List all registered agents."""
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "roles": agent._roles,
                "skill_count": len(agent._skills)
            }
            for agent in self._agents.values()
        ]
    
    def create_shared_memory(self, name: str, **kwargs):
        """Create a new shared memory repository."""
        return self.memory_manager.create_shared_memory(name, **kwargs)
    
    def get_tool_executor(self, agent_id: str) -> ToolExecutor:
        """Get a tool executor for the specified agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")
        return ToolExecutor(agent)

# Create a singleton instance
empire = Empire()
