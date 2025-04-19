"""
Tool interoperability layer for defining and executing agent tools.
"""
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints
import inspect
import functools
import json
import uuid
import logging
from pydantic import BaseModel, Field, create_model

from app.core.agent import Agent

logger = logging.getLogger(__name__)

def tool(name: Optional[str] = None, description: Optional[str] = None, 
         required_permissions: List[str] = None):
    """Decorator for registering agent tools."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(agent_instance, *args, **kwargs):
            # This simply calls the function, the actual registration is handled
            # in the Agent class when this decorator is applied to methods
            return func(agent_instance, *args, **kwargs)
        
        # Attach metadata for reflection
        wrapper._tool_metadata = {
            'name': name or func.__name__,
            'description': description or func.__doc__ or "",
            'required_permissions': required_permissions or [],
        }
        
        return wrapper
    
    return decorator

class ToolComposition:
    """Utility for composing multiple tools into a workflow."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps = []
        self.input_mappings = {}
        self.output_mappings = {}
    
    def add_step(self, tool_name: str, step_id: Optional[str] = None, 
                inputs: Dict[str, Union[str, Any]] = None):
        """Add a tool execution step to the composition."""
        step = {
            'id': step_id or f"step_{len(self.steps) + 1}",
            'tool': tool_name,
            'inputs': inputs or {}
        }
        self.steps.append(step)
        return self
    
    def map_input(self, comp_input: str, step_id: str, step_input: str):
        """Map a composition input to a specific step input."""
        if comp_input not in self.input_mappings:
            self.input_mappings[comp_input] = []
        
        self.input_mappings[comp_input].append({
            'step_id': step_id,
            'input': step_input
        })
        return self
    
    def map_output(self, step_id: str, step_output: str, comp_output: str):
        """Map a step output to a composition output."""
        self.output_mappings[comp_output] = {
            'step_id': step_id,
            'output': step_output
        }
        return self
    
    def map_step(self, from_step_id: str, from_output: str, to_step_id: str, to_input: str):
        """Map an output from one step to an input of another step."""
        # Find the destination step
        dest_step = None
        for step in self.steps:
            if step['id'] == to_step_id:
                dest_step = step
                break
        
        if not dest_step:
            raise ValueError(f"Step '{to_step_id}' not found in composition")
        
        # Set the input mapping
        dest_step['inputs'][to_input] = f"${{{from_step_id}.{from_output}}}"
        return self
    
    def build(self) -> dict:
        """Build the complete composition definition."""
        return {
            'name': self.name,
            'description': self.description,
            'steps': self.steps,
            'input_mappings': self.input_mappings,
            'output_mappings': self.output_mappings
        }

class ToolExecutionContext:
    """Context for tool execution with access to shared data and utilities."""
    
    def __init__(self, agent: Agent, execution_id: str = None):
        self.agent = agent
        self.execution_id = execution_id or str(uuid.uuid4())
        self.data = {}
        self.logs = []
    
    def set_data(self, key: str, value: Any):
        """Set a data value in the execution context."""
        self.data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get a data value from the execution context."""
        return self.data.get(key, default)
    
    def log(self, message: str, level: str = "info"):
        """Log a message in the execution context."""
        self.logs.append({
            'timestamp': '↿timestamp⇂',  # Will be replaced with actual timestamp
            'level': level,
            'message': message
        })
        
        # Also log to the system logger
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

class ToolExecutor:
    """Executor for tool compositions and individual tools."""
    
    def __init__(self, agent: Agent):
        self.agent = agent
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a single tool by name."""
        return self.agent.execute_tool(tool_name, **kwargs)
    
    def execute_composition(self, composition: Union[dict, ToolComposition], 
                           input_values: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a tool composition with the given input values."""
        # If given a ToolComposition object, convert to dict
        if isinstance(composition, ToolComposition):
            composition = composition.build()
        
        input_values = input_values or {}
        context = ToolExecutionContext(self.agent)
        
        # Store input values in context
        for key, value in input_values.items():
            context.set_data(f"input.{key}", value)
        
        # Execute each step in order
        step_results = {}
        
        for step in composition['steps']:
            step_id = step['id']
            tool_name = step['tool']
            
            # Process inputs for this step
            processed_inputs = {}
            
            for input_key, input_value in step['inputs'].items():
                # Check if it's a reference to another step's output
                if isinstance(input_value, str) and input_value.startswith("${") and input_value.endswith("}"):
                    # Extract the reference path from ${step_id.output_key}
                    ref_path = input_value[2:-1].split(".")
                    if len(ref_path) >= 2:
                        ref_step_id = ref_path[0]
                        ref_output_key = ".".join(ref_path[1:])
                        
                        if ref_step_id in step_results and ref_output_key in step_results[ref_step_id]:
                            processed_inputs[input_key] = step_results[ref_step_id][ref_output_key]
                # Check if it's a reference to a composition input
                elif isinstance(input_value, str) and input_value.startswith("$input."):
                    input_key_ref = input_value[len("$input."):]
                    if input_key_ref in input_values:
                        processed_inputs[input_key] = input_values[input_key_ref]
                else:
                    processed_inputs[input_key] = input_value
            
            # Execute the tool
            try:
                result = self.execute_tool(tool_name, **processed_inputs)
                step_results[step_id] = result if isinstance(result, dict) else {"result": result}
                
                # Store in context
                for key, value in step_results[step_id].items():
                    context.set_data(f"{step_id}.{key}", value)
                
            except Exception as e:
                context.log(f"Error executing step '{step_id}' (tool: {tool_name}): {str(e)}", "error")
                step_results[step_id] = {"error": str(e)}
                # Don't abort; continue with next steps
        
        # Process output mappings
        outputs = {}
        
        for output_key, mapping in composition.get('output_mappings', {}).items():
            step_id = mapping['step_id']
            output_path = mapping['output']
            
            if step_id in step_results:
                result = step_results[step_id]
                
                if "." in output_path:
                    # Handle nested paths like "data.results"
                    parts = output_path.split(".")
                    value = result
                    try:
                        for part in parts:
                            value = value[part]
                        outputs[output_key] = value
                    except (KeyError, TypeError):
                        outputs[output_key] = None
                else:
                    outputs[output_key] = result.get(output_path)
        
        return {
            "outputs": outputs,
            "steps": step_results,
            "logs": context.logs
        }

def compose_tools(name: str, description: str = "") -> ToolComposition:
    """Create a new tool composition."""
    return ToolComposition(name, description)
