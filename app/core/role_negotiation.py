"""
Role negotiation framework for dynamic agent role allocation and team formation.
"""
from typing import Any, Dict, List, Optional, Set, Union
import uuid
from datetime import datetime
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class RoleRequirement(BaseModel):
    """Definition of requirements for a specific role."""
    skills: Dict[str, float] = Field(default_factory=dict)  # skill_name -> minimum proficiency
    permissions: List[str] = Field(default_factory=list)
    priority: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RoleBid(BaseModel):
    """A bid from an agent for a role assignment."""
    role_id: str
    agent_id: str
    confidence: float  # 0 to 1, agent's confidence in ability to perform the role
    skill_match: Dict[str, float]  # skill -> actual proficiency
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RoleAssignment(BaseModel):
    """An assignment of a role to an agent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role_id: str
    agent_id: str
    confidence: float
    assigned_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    performance_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RoleManager:
    """Manager for role definitions, requirements, and assignments."""
    
    def __init__(self):
        self._roles = {}  # role_id -> role_name
        self._role_requirements = {}  # role_id -> RoleRequirement
        self._role_assignments = {}  # assignment_id -> RoleAssignment
        self._assignment_history = []  # List of completed assignments
    
    def register_role(self, role_id: str, requirements: RoleRequirement) -> str:
        """Register a new role with its requirements."""
        if role_id in self._roles:
            raise ValueError(f"Role '{role_id}' already registered")
            
        self._roles[role_id] = role_id
        self._role_requirements[role_id] = requirements
        return role_id
    
    def get_role_requirements(self, role_id: str) -> Optional[RoleRequirement]:
        """Get requirements for a specific role."""
        return self._role_requirements.get(role_id)
    
    def list_roles(self) -> List[str]:
        """List all registered roles."""
        return list(self._roles.keys())
    
    def evaluate_agent_for_role(self, agent, role_id: str) -> Dict[str, Any]:
        """Evaluate an agent's suitability for a role."""
        if role_id not in self._roles:
            raise ValueError(f"Unknown role: {role_id}")
        
        requirements = self._role_requirements[role_id]
        agent_skills = agent.get_skills()
        
        # Check skill requirements
        skill_match = {}
        missing_skills = []
        total_match_score = 0
        required_skill_count = 0
        
        for skill, min_proficiency in requirements.skills.items():
            required_skill_count += 1
            agent_proficiency = agent_skills.get(skill, 0)
            skill_match[skill] = agent_proficiency
            
            if agent_proficiency < min_proficiency:
                missing_skills.append((skill, min_proficiency, agent_proficiency))
            else:
                # Calculate how well the agent exceeds the minimum requirement
                match_quality = min(1.0, agent_proficiency / (min_proficiency or 0.1))
                total_match_score += match_quality
        
        # Check permission requirements
        missing_permissions = [p for p in requirements.permissions if p not in agent.permissions]
        
        # Calculate overall confidence score
        confidence = 0.0
        if required_skill_count > 0:
            # Base confidence on average skill match
            confidence = total_match_score / required_skill_count
            
            # Penalize for missing skills or permissions
            if missing_skills:
                confidence *= (1.0 - (len(missing_skills) / required_skill_count) * 0.5)
            if missing_permissions:
                confidence *= (0.8 ** len(missing_permissions))
        
        return {
            "agent_id": agent.agent_id,
            "role_id": role_id,
            "confidence": confidence,
            "skill_match": skill_match,
            "missing_skills": missing_skills,
            "missing_permissions": missing_permissions,
            "qualified": not missing_skills and not missing_permissions
        }
    
    def create_bid(self, agent, role_id: str) -> RoleBid:
        """Create a bid for a role based on agent's suitability."""
        evaluation = self.evaluate_agent_for_role(agent, role_id)
        
        return RoleBid(
            role_id=role_id,
            agent_id=agent.agent_id,
            confidence=evaluation["confidence"],
            skill_match=evaluation["skill_match"]
        )
    
    def assign_role(self, role_id: str, agent_id: str, confidence: float, 
                   expires_at: Optional[datetime] = None, metadata: Dict[str, Any] = None) -> str:
        """Assign a role to an agent."""
        assignment = RoleAssignment(
            role_id=role_id,
            agent_id=agent_id,
            confidence=confidence,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._role_assignments[assignment.id] = assignment
        return assignment.id
    
    def get_assignment(self, assignment_id: str) -> Optional[RoleAssignment]:
        """Get a role assignment by ID."""
        return self._role_assignments.get(assignment_id)
    
    def complete_assignment(self, assignment_id: str, performance_score: float) -> bool:
        """Mark a role assignment as completed with a performance score."""
        if assignment_id not in self._role_assignments:
            return False
            
        assignment = self._role_assignments[assignment_id]
        assignment.performance_score = performance_score
        
        # Move to history
        self._assignment_history.append(assignment)
        del self._role_assignments[assignment_id]
        
        return True
    
    def revoke_assignment(self, assignment_id: str) -> bool:
        """Revoke a role assignment."""
        if assignment_id not in self._role_assignments:
            return False
            
        del self._role_assignments[assignment_id]
        return True
    
    def get_active_assignments_for_role(self, role_id: str) -> List[RoleAssignment]:
        """Get all active assignments for a specific role."""
        return [a for a in self._role_assignments.values() if a.role_id == role_id]
    
    def get_active_assignments_for_agent(self, agent_id: str) -> List[RoleAssignment]:
        """Get all active role assignments for a specific agent."""
        return [a for a in self._role_assignments.values() if a.agent_id == agent_id]
    
    def get_role_performance_history(self, role_id: str) -> List[Dict[str, Any]]:
        """Get performance history for a specific role."""
        role_history = [a for a in self._assignment_history if a.role_id == role_id]
        
        return [
            {
                "assignment_id": a.id,
                "agent_id": a.agent_id,
                "confidence": a.confidence,
                "performance_score": a.performance_score,
                "assigned_at": a.assigned_at,
                "completed_at": datetime.now()  # Approximate
            }
            for a in role_history
        ]
    
    def get_agent_role_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get an agent's role assignment history."""
        agent_history = [a for a in self._assignment_history if a.agent_id == agent_id]
        
        return [
            {
                "assignment_id": a.id,
                "role_id": a.role_id,
                "confidence": a.confidence,
                "performance_score": a.performance_score,
                "assigned_at": a.assigned_at,
                "completed_at": datetime.now()  # Approximate
            }
            for a in agent_history
        ]

class TeamFormation:
    """Team formation and management for multi-agent tasks."""
    
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager
        self.teams = {}  # team_id -> {"name": str, "roles": Dict[role_id -> assignment_id]}
        
    def create_team(self, team_id: str, name: str) -> str:
        """Create a new team."""
        if team_id in self.teams:
            raise ValueError(f"Team '{team_id}' already exists")
            
        self.teams[team_id] = {
            "name": name,
            "roles": {},
            "metadata": {}
        }
        return team_id
    
    def assign_role_to_team(self, team_id: str, role_id: str, agent_id: str, 
                           confidence: float, metadata: Dict[str, Any] = None) -> str:
        """Assign a role to an agent within a team."""
        if team_id not in self.teams:
            raise ValueError(f"Team '{team_id}' does not exist")
            
        # Create the assignment
        assignment_id = self.role_manager.assign_role(
            role_id=role_id,
            agent_id=agent_id,
            confidence=confidence,
            metadata={**(metadata or {}), "team_id": team_id}
        )
        
        # Add to team
        self.teams[team_id]["roles"][role_id] = assignment_id
        return assignment_id
    
    def remove_role_from_team(self, team_id: str, role_id: str) -> bool:
        """Remove a role assignment from a team."""
        if team_id not in self.teams or role_id not in self.teams[team_id]["roles"]:
            return False
            
        # Revoke the assignment
        assignment_id = self.teams[team_id]["roles"][role_id]
        self.role_manager.revoke_assignment(assignment_id)
        
        # Remove from team
        del self.teams[team_id]["roles"][role_id]
        return True
    
    def get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all members of a team with their roles."""
        if team_id not in self.teams:
            raise ValueError(f"Team '{team_id}' does not exist")
            
        members = []
        for role_id, assignment_id in self.teams[team_id]["roles"].items():
            assignment = self.role_manager.get_assignment(assignment_id)
            if assignment:
                members.append({
                    "role_id": role_id,
                    "agent_id": assignment.agent_id,
                    "assignment_id": assignment_id,
                    "confidence": assignment.confidence
                })
                
        return members
    
    def disband_team(self, team_id: str) -> bool:
        """Disband a team, revoking all role assignments."""
        if team_id not in self.teams:
            return False
            
        # Revoke all assignments
        for role_id, assignment_id in self.teams[team_id]["roles"].items():
            self.role_manager.revoke_assignment(assignment_id)
            
        # Remove team
        del self.teams[team_id]
        return True
    
    def list_teams(self) -> List[Dict[str, Any]]:
        """List all teams with basic information."""
        return [
            {
                "team_id": team_id,
                "name": team_info["name"],
                "role_count": len(team_info["roles"]),
                "metadata": team_info.get("metadata", {})
            }
            for team_id, team_info in self.teams.items()
        ]
    
    def evaluate_team_performance(self, team_id: str) -> Dict[str, Any]:
        """Evaluate overall team performance based on role assignments."""
        if team_id not in self.teams:
            raise ValueError(f"Team '{team_id}' does not exist")
            
        # Get performance metrics for all team members
        total_confidence = 0.0
        assignments = []
        
        for role_id, assignment_id in self.teams[team_id]["roles"].items():
            assignment = self.role_manager.get_assignment(assignment_id)
            if assignment:
                total_confidence += assignment.confidence
                assignments.append(assignment)
                
        avg_confidence = total_confidence / len(assignments) if assignments else 0
        
        return {
            "team_id": team_id,
            "name": self.teams[team_id]["name"],
            "member_count": len(assignments),
            "avg_confidence": avg_confidence,
            "members": [
                {
                    "role_id": a.role_id,
                    "agent_id": a.agent_id,
                    "confidence": a.confidence
                }
                for a in assignments
            ]
        }
