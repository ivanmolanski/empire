"""
Core Agent class that provides the foundation for specialized agents in the system.
Implements tool registration, execution, and inter-agent communication protocols.
"""
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints
import inspect
import functools
import uuid
from datetime import datetime
import logging
from pydantic import BaseModel, Field, create_model

logger = logging.getLogger(__name__)

class AgentContext(BaseModel):
    """Context object passed between agents during communication."""
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    message_type: str = "default"
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)

class ToolRegistryMeta(type):
    """Metaclass to ensure tool registry singletons per agent type."""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ToolRegistry(metaclass=ToolRegistryMeta):
    """Registry for agent tools with validation and metadata management."""
    def __init__(self):
        self.tools = {}
        
    def register(self, func=None, *, name: Optional[str] = None, 
                description: Optional[str] = None, 
                required_permissions: List[str] = None):
        """Decorator for registering tools with the registry."""
        def decorator(func):
            tool_name = name or func.__name__
            func_sig = inspect.signature(func)
            
            # Extract parameter types using type hints
            type_hints = get_type_hints(func)
            
            # Build input model dynamically
            field_definitions = {}
            for param_name, param in func_sig.parameters.items():
                if param_name == 'self':  # Skip self parameter
                    continue
                
                param_type = type_hints.get(param_name, Any)
                default_value = ... if param.default is inspect.Parameter.empty else param.default
                
                field_definitions[param_name] = (param_type, default_value)
            
            # Create input and output models
            input_model = create_model(f"{tool_name}Input", **field_definitions)
            output_type = type_hints.get('return', Any)
            
            # Store tool metadata
            self.tools[tool_name] = {
                'function': func,
                'name': tool_name,
                'description': description or func.__doc__ or "",
                'input_model': input_model,
                'output_type': output_type,
                'required_permissions': required_permissions or []
            }
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Validate inputs using the dynamic Pydantic model
                if args and isinstance(args[0], Agent):  # If called from an agent instance
                    instance = args[0]
                    other_args = args[1:]
                    
                    # Combine positional and keyword arguments
                    combined_kwargs = {**{k: v for k, v in zip(list(field_definitions.keys()), other_args)}, **kwargs}
                    
                    # Create model instance for validation
                    try:
                        model_instance = input_model(**combined_kwargs)
                        validated_kwargs = model_instance.dict()
                        
                        # Log the tool execution for accountability
                        instance._log_tool_execution(
                            tool_name=tool_name,
                            inputs=validated_kwargs,
                            source="direct_call"
                        )
                        
                        result = func(instance, **validated_kwargs)
                        return result
                    except Exception as e:
                        instance._log_error(f"Tool validation error: {str(e)}")
                        raise
                else:
                    # Direct function call (not through an agent)
                    return func(*args, **kwargs)
            
            return wrapper
        
        # Handle both @register and @register() syntax
        if func is None:
            return decorator
        return decorator(func)

    def get_tool_schema(self, tool_name):
        """Get JSON schema for a tool's inputs and outputs."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
            
        tool = self.tools[tool_name]
        return {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_model"].schema(),
            "required_permissions": tool["required_permissions"]
        }
    
    def list_tools(self):
        """Return a list of all registered tools with their metadata."""
        return [
            {
                "name": name,
                "description": tool["description"],
                "required_permissions": tool["required_permissions"]
            }
            for name, tool in self.tools.items()
        ]

class Agent:
    """Base agent class with tool registration, execution, and communication capabilities."""
    
    def __init__(self, agent_id: str = None, name: str = None):
        """Initialize a new agent with optional ID and name."""
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent-{self.agent_id[:8]}"
        self.tools = ToolRegistry()
        self.memory = {}  # Simple memory storage
        self.permissions = []
        self._execution_history = []
        self._communication_channels = {}
        self._roles = set()
        self._skills = {}
        self._accountability_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_response_time": 0.0,
            "reliability_score": 1.0  # Scale from 0 to 1
        }
        self._collaboration_scores = {}  # Store scores for other agents
        
    def register_tool(self, *args, **kwargs):
        """Register a new tool method for this agent."""
        return self.tools.register(*args, **kwargs)
        
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool by name with given arguments."""
        if tool_name not in self.tools.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        
        tool_info = self.tools.tools[tool_name]
        required_permissions = tool_info.get('required_permissions', [])
        
        # Check permissions
        for permission in required_permissions:
            if permission not in self.permissions:
                raise PermissionError(f"Agent lacks required permission: {permission}")
        
        # Log execution intent for accountability
        self._log_tool_execution(
            tool_name=tool_name,
            inputs=kwargs,
            source="execute_tool"
        )
        
        # Execute tool and log
        start_time = datetime.now()
        try:
            result = tool_info['function'](self, **kwargs)
            status = "success"
            self._accountability_metrics["tasks_completed"] += 1
            
            # Update reliability score
            tasks_total = self._accountability_metrics["tasks_completed"] + self._accountability_metrics["tasks_failed"]
            self._accountability_metrics["reliability_score"] = self._accountability_metrics["tasks_completed"] / tasks_total
            
            return result
        except Exception as e:
            status = f"error: {str(e)}"
            self._accountability_metrics["tasks_failed"] += 1
            
            # Update reliability score
            tasks_total = self._accountability_metrics["tasks_completed"] + self._accountability_metrics["tasks_failed"]
            self._accountability_metrics["reliability_score"] = self._accountability_metrics["tasks_completed"] / tasks_total
            
            logger.error(f"Agent {self.agent_id} tool execution error: {str(e)}")
            raise
        finally:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update response time metric for accountability
            if self._accountability_metrics["avg_response_time"] == 0.0:
                self._accountability_metrics["avg_response_time"] = execution_time
            else:
                # Rolling average
                avg = self._accountability_metrics["avg_response_time"]
                total_tasks = self._accountability_metrics["tasks_completed"] + self._accountability_metrics["tasks_failed"]
                self._accountability_metrics["avg_response_time"] = (avg * (total_tasks - 1) + execution_time) / total_tasks
            
            # Add to execution history
            execution_record = {
                "tool": tool_name,
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "status": status
            }
            self._execution_history.append(execution_record)
    
    def _log_tool_execution(self, tool_name: str, inputs: Dict[str, Any], source: str):
        """Log tool execution for accountability and tracing."""
        logger.info(f"Agent {self.agent_id} executing tool '{tool_name}' (source: {source})")
    
    def _log_error(self, error_message: str):
        """Log error message for this agent."""
        logger.error(f"Agent {self.agent_id}: {error_message}")
    
    def set_skill(self, skill_name: str, proficiency: float):
        """Set proficiency level for a specific skill."""
        if not 0 <= proficiency <= 1:
            raise ValueError("Proficiency must be between 0 and 1")
        self._skills[skill_name] = proficiency
        
    def assign_role(self, role_name: str):
        """Assign a role to this agent."""
        self._roles.add(role_name)
        
    def has_role(self, role_name: str) -> bool:
        """Check if agent has the specified role."""
        return role_name in self._roles
    
    def get_skills(self) -> Dict[str, float]:
        """Get all skills and proficiency levels."""
        return self._skills.copy()
    
    def has_skill(self, skill_name: str, min_proficiency: float = 0) -> bool:
        """Check if agent has the specified skill at minimum proficiency level."""
        return self._skills.get(skill_name, 0) >= min_proficiency
    
    def update_collaboration_score(self, agent_id: str, score_delta: float):
        """Update collaboration score for another agent based on interaction."""
        current_score = self._collaboration_scores.get(agent_id, 0.5)  # Default neutral score
        
        # Ensure score stays in valid range
        new_score = max(0, min(1, current_score + score_delta))
        self._collaboration_scores[agent_id] = new_score
    
    def get_accountability_metrics(self) -> Dict[str, Any]:
        """Get accountability metrics for this agent."""
        return self._accountability_metrics.copy()
    
    def get_collaboration_score(self, agent_id: str) -> float:
        """Get collaboration score for another agent."""
        return self._collaboration_scores.get(agent_id, 0.5)  # Default neutral score

    def __repr__(self):
        return f"{self.name} ({self.agent_id})"
