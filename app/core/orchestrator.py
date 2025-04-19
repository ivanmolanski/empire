"""
Workflow orchestration engine for coordinating multi-agent execution flows.
"""
from typing import Any, Callable, Dict, List, Optional, Set, Union
import asyncio
import uuid
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from app.core.agent import Agent, AgentContext
from app.core.communication import MessageBus
from app.core.role_negotiation import RoleManager, RoleRequirement

logger = logging.getLogger(__name__)

class WorkflowStep(BaseModel):
    """Definition of a single step in a workflow."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    role_required: Optional[str] = None
    tool_required: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    output_mapping: Dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = 60
    retry_count: int = 0
    on_failure: Optional[str] = None  # ID of step to execute on failure
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowDefinition(BaseModel):
    """Definition of a complete workflow."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0"
    steps: List[WorkflowStep] = Field(default_factory=list)
    transitions: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    initial_step_id: Optional[str] = None
    on_complete: Optional[Callable] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

class WorkflowInstance(BaseModel):
    """Runtime instance of a workflow execution."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: str = "pending"  # pending, running, completed, failed, cancelled
    current_step_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    agent_assignments: Dict[str, str] = Field(default_factory=dict)  # step_id -> agent_id
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Orchestrator:
    """Workflow orchestration engine for coordinating multi-agent execution."""
    
    def __init__(self, message_bus: MessageBus, role_manager: RoleManager):
        self.message_bus = message_bus
        self.role_manager = role_manager
        self.workflows = {}  # workflow_id -> WorkflowDefinition
        self.instances = {}  # instance_id -> WorkflowInstance
        self.agents = {}  # agent_id -> Agent
        self._event_listeners = {}  # event_type -> list of callbacks
    
    def register_agent(self, agent: Agent):
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
    
    def register_workflow(self, workflow: WorkflowDefinition) -> str:
        """Register a workflow definition."""
        self.workflows[workflow.id] = workflow
        return workflow.id
    
    def create_workflow(self, name: str, description: str = "", version: str = "1.0") -> WorkflowDefinition:
        """Create a new workflow definition."""
        workflow = WorkflowDefinition(
            name=name,
            description=description,
            version=version
        )
        self.workflows[workflow.id] = workflow
        return workflow
    
    def start_workflow(self, workflow_id: str, initial_context: Dict[str, Any] = None) -> str:
        """Start a new instance of a workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        workflow = self.workflows[workflow_id]
        
        # Create workflow instance
        instance = WorkflowInstance(
            workflow_id=workflow_id,
            context=initial_context or {},
            status="pending"
        )
        self.instances[instance.id] = instance
        
        # Determine initial step
        if workflow.initial_step_id:
            initial_step_id = workflow.initial_step_id
        elif workflow.steps:
            initial_step_id = workflow.steps[0].id
        else:
            raise ValueError(f"Workflow '{workflow_id}' has no steps")
        
        # Schedule execution
        asyncio.create_task(self._execute_workflow_instance(instance.id, initial_step_id))
        
        return instance.id
    
    async def _execute_workflow_instance(self, instance_id: str, initial_step_id: str):
        """Execute a workflow instance."""
        if instance_id not in self.instances:
            logger.error(f"Workflow instance '{instance_id}' not found")
            return
        
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        # Update instance state
        instance.status = "running"
        instance.started_at = datetime.now()
        instance.current_step_id = initial_step_id
        
        # Trigger event
        self._trigger_event("workflow_started", {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id
        })
        
        # Find initial step
        step_id = initial_step_id
        step = None
        
        # Execute steps until completion or failure
        while step_id:
            # Find current step
            step = next((s for s in workflow.steps if s.id == step_id), None)
            if not step:
                self._fail_workflow_instance(instance_id, f"Step '{step_id}' not found in workflow definition")
                return
            
            # Update instance state
            instance.current_step_id = step_id
            
            # Execute step
            try:
                result = await self._execute_workflow_step(instance_id, step_id)
                
                # Store result
                instance.step_results[step_id] = result
                
                # Determine next step
                if step_id in workflow.transitions:
                    transitions = workflow.transitions[step_id]
                    result_key = result.get("status", "default")
                    
                    if result_key in transitions:
                        step_id = transitions[result_key]
                    elif "default" in transitions:
                        step_id = transitions["default"]
                    else:
                        step_id = None  # No valid transition found
                else:
                    step_id = None  # No transitions defined for this step
                
            except Exception as e:
                logger.error(f"Error executing step '{step_id}' in workflow instance '{instance_id}': {str(e)}")
                
                # Check if failure handling is defined
                if step.on_failure:
                    step_id = step.on_failure
                    instance.errors.append({
                        "step_id": step_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    # Fail the workflow
                    self._fail_workflow_instance(instance_id, f"Step execution error: {str(e)}")
                    return
        
        # Workflow completed
        self._complete_workflow_instance(instance_id)
    
    async def _execute_workflow_step(self, instance_id: str, step_id: str) -> Dict[str, Any]:
        """Execute a single workflow step."""
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        # Find step definition
        step = next((s for s in workflow.steps if s.id == step_id), None)
        if not step:
            raise ValueError(f"Step '{step_id}' not found in workflow definition")
        
        # Trigger event
        self._trigger_event("step_started", {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id,
            "step_id": step_id
        })
        
        # Resolve inputs by substituting context variables
        resolved_inputs = {}
        for key, value in step.inputs.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Extract path from ${context.path.to.value}
                path = value[2:-1].split(".")
                context_value = instance.context
                
                try:
                    for path_part in path:
                        context_value = context_value[path_part]
                    resolved_inputs[key] = context_value
                except (KeyError, TypeError):
                    logger.warning(f"Failed to resolve context variable '{value}' for input '{key}'")
                    resolved_inputs[key] = None
            else:
                resolved_inputs[key] = value
        
        # Determine agent to execute step
        agent_id = None
        
        if step_id in instance.agent_assignments:
            # Use pre-assigned agent
            agent_id = instance.agent_assignments[step_id]
        elif step.role_required:
            # Get agent by role
            assignments = self.role_manager.get_active_assignments_for_role(step.role_required)
            if assignments:
                # For now, just take the first assignment
                agent_id = assignments[0].agent_id
        
        if not agent_id or agent_id not in self.agents:
            # No valid agent found
            raise ValueError(f"No suitable agent found for step '{step_id}'")
        
        agent = self.agents[agent_id]
        
        # Execute tool
        if step.tool_required:
            start_time = datetime.now()
            
            try:
                # Execute with timeout
                result = agent.execute_tool(step.tool_required, **resolved_inputs)
                execution_time = (datetime.now() - start_time).total_seconds()
                status = "success"
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                status = "error"
                raise
            
            # Process result
            if isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {"result": result}
                
            # Add execution metadata
            result_dict["status"] = status
            result_dict["execution_time"] = execution_time
            result_dict["agent_id"] = agent_id
            
            # Map outputs to context
            self._map_step_outputs_to_context(instance_id, step, result_dict)
            
            # Trigger event
            self._trigger_event("step_completed", {
                "instance_id": instance_id,
                "workflow_id": instance.workflow_id,
                "step_id": step_id,
                "status": status,
                "execution_time": execution_time
            })
            
            return result_dict
        else:
            # No tool specified, just a pass-through step
            result = {"status": "success"}
            
            # Map any static outputs to context
            self._map_step_outputs_to_context(instance_id, step, result)
            
            # Trigger event
            self._trigger_event("step_completed", {
                "instance_id": instance_id,
                "workflow_id": instance.workflow_id,
                "step_id": step_id,
                "status": "success"
            })
            
            return result
    
    def _map_step_outputs_to_context(self, instance_id: str, step: WorkflowStep, result: Dict[str, Any]):
        """Map step outputs to workflow context based on output_mapping."""
        instance = self.instances[instance_id]
        
        for output_path, context_path in step.output_mapping.items():
            # Parse output path (e.g., "result.data.value" or just "$" for the entire result)
            if output_path == "$":
                output_value = result
            else:
                output_parts = output_path.split(".")
                output_value = result
                
                try:
                    for part in output_parts:
                        output_value = output_value[part]
                except (KeyError, TypeError):
                    logger.warning(f"Failed to resolve output path '{output_path}'")
                    continue
            
            # Parse context path (e.g., "results.step_name.value")
            context_parts = context_path.split(".")
            if not context_parts:
                continue
                
            # Navigate to the right level in the context
            context_ref = instance.context
            for i, part in enumerate(context_parts[:-1]):
                if part not in context_ref:
                    context_ref[part] = {}
                context_ref = context_ref[part]
                
            # Set the value
            context_ref[context_parts[-1]] = output_value
    
    def _complete_workflow_instance(self, instance_id: str):
        """Mark a workflow instance as completed."""
        if instance_id not in self.instances:
            return
            
        instance = self.instances[instance_id]
        instance.status = "completed"
        instance.completed_at = datetime.now()
        
        # Trigger event
        self._trigger_event("workflow_completed", {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id
        })
        
        # Execute completion callback if defined
        workflow = self.workflows[instance.workflow_id]
        if workflow.on_complete:
            try:
                workflow.on_complete(instance)
            except Exception as e:
                logger.error(f"Error in workflow completion callback: {str(e)}")
    
    def _fail_workflow_instance(self, instance_id: str, error_message: str):
        """Mark a workflow instance as failed."""
        if instance_id not in self.instances:
            return
            
        instance = self.instances[instance_id]
        instance.status = "failed"
        instance.completed_at = datetime.now()
        instance.errors.append({
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger event
        self._trigger_event("workflow_failed", {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id,
            "error": error_message
        })
    
    def cancel_workflow_instance(self, instance_id: str) -> bool:
        """Cancel a running workflow instance."""
        if instance_id not in self.instances:
            return False
            
        instance = self.instances[instance_id]
        if instance.status not in ["pending", "running"]:
            return False
            
        instance.status = "cancelled"
        instance.completed_at = datetime.now()
        
        # Trigger event
        self._trigger_event("workflow_cancelled", {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id
        })
        
        return True
    
    def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow instance."""
        if instance_id not in self.instances:
            raise ValueError(f"Workflow instance '{instance_id}' not found")
            
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        # Calculate progress
        total_steps = len(workflow.steps)
        completed_steps = len(instance.step_results)
        progress = (completed_steps / total_steps) if total_steps > 0 else 0
        
        return {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id,
            "workflow_name": workflow.name,
            "status": instance.status,
            "progress": progress,
            "current_step": instance.current_step_id,
            "created_at": instance.created_at.isoformat(),
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "error_count": len(instance.errors)
        }
    
    def get_workflow_results(self, instance_id: str) -> Dict[str, Any]:
        """Get the results of a completed workflow instance."""
        if instance_id not in self.instances:
            raise ValueError(f"Workflow instance '{instance_id}' not found")
            
        instance = self.instances[instance_id]
        
        return {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id,
            "status": instance.status,
            "context": instance.context,
            "step_results": instance.step_results,
            "errors": instance.errors,
            "created_at": instance.created_at.isoformat(),
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None
        }
    
    def list_workflow_instances(self, workflow_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """List workflow instances, optionally filtered by workflow ID or status."""
        instances = self.instances.values()
        
        if workflow_id:
            instances = [i for i in instances if i.workflow_id == workflow_id]
            
        if status:
            instances = [i for i in instances if i.status == status]
            
        return [
            {
                "instance_id": i.id,
                "workflow_id": i.workflow_id,
                "workflow_name": self.workflows[i.workflow_id].name,
                "status": i.status,
                "created_at": i.created_at.isoformat(),
                "completed_at": i.completed_at.isoformat() if i.completed_at else None
            }
            for i in instances
        ]
    
    def on(self, event_type: str, callback: Callable):
        """Register an event listener."""
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger an event to all registered listeners."""
        if event_type in self._event_listeners:
            for callback in self._event_listeners[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    logger.error(f"Error in event listener for '{event_type}': {str(e)}")
                    
        # Also log the event
        logger.info(f"Workflow event: {event_type} - {event_data}")
    
    def assign_agent_to_step(self, instance_id: str, step_id: str, agent_id: str) -> bool:
        """Explicitly assign an agent to execute a specific step."""
        if instance_id not in self.instances:
            return False
            
        if agent_id not in self.agents:
            return False
            
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        # Verify step exists
        if not any(s.id == step_id for s in workflow.steps):
            return False
            
        instance.agent_assignments[step_id] = agent_id
        return True
