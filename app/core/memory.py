"""
Memory management system for agents to store, retrieve, and forget information.
"""
from typing import Any, Dict, List, Optional, Union, Tuple
import uuid
from datetime import datetime
import logging
import json
from pydantic import BaseModel, Field
import heapq

logger = logging.getLogger(__name__)

class MemoryItem(BaseModel):
    """A single memory item with metadata for retrieval and importance scoring."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: Any
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)
    expiration: Optional[datetime] = None
    importance: float = 0.5  # 0 to 1, higher is more important
    tags: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if memory has expired."""
        if not self.expiration:
            return False
        return datetime.now() > self.expiration
    
    def decay_importance(self, decay_factor: float):
        """Decay the importance of this memory over time."""
        self.importance = max(0, self.importance * decay_factor)
        
    def calculate_relevance(self, query_vector, embedding_function=None) -> float:
        """Calculate relevance score against a query, if embedding functions are available."""
        if embedding_function is None:
            # Without embedding function, use simple tag matching
            query_terms = query_vector.lower().split() if isinstance(query_vector, str) else []
            if not query_terms:
                return 0.0
            
            matches = 0
            for tag in self.tags:
                for term in query_terms:
                    if term in tag.lower():
                        matches += 1
            
            # Simple relevance score based on tag matches
            return min(1.0, matches / len(query_terms))
        else:
            # Use embedding function for semantic similarity
            try:
                content_str = json.dumps(self.content) if not isinstance(self.content, str) else self.content
                content_vector = embedding_function(content_str)
                return embedding_function.similarity(content_vector, query_vector)
            except Exception as e:
                logger.error(f"Error calculating semantic similarity: {str(e)}")
                return 0.0

class AgentMemory:
    """Memory management for agents with importance-based organization."""
    
    def __init__(self, max_size: int = 1000, decay_rate: float = 0.99):
        self.memories = {}  # id -> MemoryItem
        self.max_size = max_size
        self.decay_rate = decay_rate
        self._embedding_function = None
        self._tags_index = {}  # tag -> set(memory_ids)
        self._context_index = {}  # context_key:context_value -> set(memory_ids)
    
    def store(self, content: Any, source: str, importance: float = 0.5, tags: List[str] = None, 
              context: Dict[str, Any] = None, expiration: datetime = None, metadata: Dict[str, Any] = None) -> str:
        """Store a new memory item."""
        if len(self.memories) >= self.max_size:
            self._forget_least_important()
        
        memory = MemoryItem(
            content=content,
            source=source,
            importance=importance,
            tags=tags or [],
            context=context or {},
            expiration=expiration,
            metadata=metadata or {}
        )
        
        self.memories[memory.id] = memory
        
        # Update indexes for efficient retrieval
        for tag in memory.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = set()
            self._tags_index[tag].add(memory.id)
        
        for key, value in memory.context.items():
            index_key = f"{key}:{value}"
            if index_key not in self._context_index:
                self._context_index[index_key] = set()
            self._context_index[index_key].add(memory.id)
        
        return memory.id
    
    def retrieve(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory by ID."""
        memory = self.memories.get(memory_id)
        if memory and not memory.is_expired():
            return memory
        elif memory and memory.is_expired():
            del self.memories[memory_id]
        return None
    
    def search_by_tags(self, tags: List[str], require_all: bool = False) -> List[MemoryItem]:
        """Search memories by tags."""
        if not tags:
            return []
            
        candidate_ids = set()
        for tag in tags:
            tag_matches = set()
            for indexed_tag, memory_ids in self._tags_index.items():
                if tag.lower() in indexed_tag.lower():
                    tag_matches.update(memory_ids)
            
            if not candidate_ids:
                candidate_ids = tag_matches
            elif require_all:
                candidate_ids = candidate_ids.intersection(tag_matches)
            else:
                candidate_ids = candidate_ids.union(tag_matches)
                
        results = []
        for memory_id in candidate_ids:
            memory = self.retrieve(memory_id)
            if memory:  # This ensures expired memories are not included
                results.append(memory)
                
        # Sort by importance
        results.sort(key=lambda x: x.importance, reverse=True)
        return results
    
    def search_by_context(self, context: Dict[str, Any]) -> List[MemoryItem]:
        """Search memories by context attributes."""
        if not context:
            return []
            
        candidate_ids = set()
        first_key = True
        
        for key, value in context.items():
            index_key = f"{key}:{value}"
            if index_key in self._context_index:
                if first_key:
                    candidate_ids = self._context_index[index_key].copy()
                    first_key = False
                else:
                    candidate_ids = candidate_ids.intersection(self._context_index[index_key])
                    
            if first_key:
                # No matches found
                return []
                
        results = []
        for memory_id in candidate_ids:
            memory = self.retrieve(memory_id)
            if memory:
                results.append(memory)
                
        # Sort by importance
        results.sort(key=lambda x: x.importance, reverse=True)
        return results
    
    def search_by_relevance(self, query: str, limit: int = 5) -> List[Tuple[MemoryItem, float]]:
        """Search memories by relevance to query, return memories with scores."""
        if not query:
            return []
            
        # Calculate relevance for all non-expired memories
        scored_memories = []
        for memory_id, memory in list(self.memories.items()):
            if memory.is_expired():
                del self.memories[memory_id]
                continue
                
            relevance = memory.calculate_relevance(query, self._embedding_function)
            # Combined score considering both relevance and importance
            combined_score = (relevance * 0.7) + (memory.importance * 0.3)
            scored_memories.append((memory, combined_score))
            
        # Sort by combined score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return scored_memories[:limit]
    
    def update(self, memory_id: str, **updates) -> bool:
        """Update an existing memory with new attributes."""
        memory = self.retrieve(memory_id)
        if not memory:
            return False
            
        # Handle special updates
        if 'importance' in updates and isinstance(updates['importance'], float):
            memory.importance = max(0, min(1, updates['importance']))
            
        if 'tags' in updates and isinstance(updates['tags'], list):
            # Remove memory from old tag indexes
            for tag in memory.tags:
                if tag in self._tags_index:
                    self._tags_index[tag].discard(memory_id)
            
            memory.tags = updates['tags']
            
            # Add to new tag indexes
            for tag in memory.tags:
                if tag not in self._tags_index:
                    self._tags_index[tag] = set()
                self._tags_index[tag].add(memory_id)
                
        if 'context' in updates and isinstance(updates['context'], dict):
            # Remove from old context indexes
            for key, value in memory.context.items():
                index_key = f"{key}:{value}"
                if index_key in self._context_index:
                    self._context_index[index_key].discard(memory_id)
                    
            memory.context = updates['context']
            
            # Add to new context indexes
            for key, value in memory.context.items():
                index_key = f"{key}:{value}"
                if index_key not in self._context_index:
                    self._context_index[index_key] = set()
                self._context_index[index_key].add(memory_id)
                
        # Update other attributes
        for key, value in updates.items():
            if key not in ['importance', 'tags', 'context'] and hasattr(memory, key):
                setattr(memory, key, value)
                
        return True
    
    def forget(self, memory_id: str) -> bool:
        """Explicitly forget a memory."""
        if memory_id not in self.memories:
            return False
            
        memory = self.memories[memory_id]
        
        # Remove from indexes
        for tag in memory.tags:
            if tag in self._tags_index:
                self._tags_index[tag].discard(memory_id)
                
        for key, value in memory.context.items():
            index_key = f"{key}:{value}"
            if index_key in self._context_index:
                self._context_index[index_key].discard(memory_id)
                
        # Remove the memory
        del self.memories[memory_id]
        return True
    
    def decay_all(self):
        """Apply decay to all memories based on the decay rate."""
        for memory in list(self.memories.values()):
            memory.decay_importance(self.decay_rate)
            
            # Remove memories whose importance has decayed below threshold
            if memory.importance < 0.05:
                self.forget(memory.id)
    
    def _forget_least_important(self):
        """Forget the least important memories when capacity is reached."""
        if not self.memories:
            return
            
        # Sort memories by importance
        sorted_memories = sorted(self.memories.values(), key=lambda x: x.importance)
        
        # Remove least important ones (5% of capacity or at least 1)
        removal_count = max(1, int(self.max_size * 0.05))
        for i in range(min(removal_count, len(sorted_memories))):
            self.forget(sorted_memories[i].id)
    
    def set_embedding_function(self, func):
        """Set the embedding function for semantic similarity."""
        self._embedding_function = func
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        tags_count = {}
        sources_count = {}
        total_importance = 0
        
        for memory in self.memories.values():
            for tag in memory.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
                
            sources_count[memory.source] = sources_count.get(memory.source, 0) + 1
            total_importance += memory.importance
            
        avg_importance = total_importance / len(self.memories) if self.memories else 0
        
        return {
            "memory_count": len(self.memories),
            "capacity": self.max_size,
            "top_tags": dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "sources": sources_count,
            "avg_importance": avg_importance
        }

class SharedMemory:
    """A shared memory repository accessible by multiple agents."""
    
    def __init__(self, name: str, max_size: int = 10000):
        self.name = name
        self.memory = AgentMemory(max_size=max_size)
        self._access_permissions = {}  # agent_id -> {'read': bool, 'write': bool}
        
    def grant_access(self, agent_id: str, read: bool = True, write: bool = False):
        """Grant memory access permissions to an agent."""
        self._access_permissions[agent_id] = {'read': read, 'write': write}
        
    def revoke_access(self, agent_id: str):
        """Revoke all memory access from an agent."""
        if agent_id in self._access_permissions:
            del self._access_permissions[agent_id]
            
    def has_read_access(self, agent_id: str) -> bool:
        """Check if agent has read access."""
        return agent_id in self._access_permissions and self._access_permissions[agent_id]['read']
        
    def has_write_access(self, agent_id: str) -> bool:
        """Check if agent has write access."""
        return agent_id in self._access_permissions and self._access_permissions[agent_id]['write']
    
    def store(self, agent_id: str, content: Any, **kwargs) -> Optional[str]:
        """Store a memory if agent has write access."""
        if not self.has_write_access(agent_id):
            logger.warning(f"Agent {agent_id} attempted to write to shared memory {self.name} without permission")
            return None
            
        return self.memory.store(content=content, source=f"agent:{agent_id}", **kwargs)
        
    def retrieve(self, agent_id: str, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory if agent has read access."""
        if not self.has_read_access(agent_id):
            logger.warning(f"Agent {agent_id} attempted to read from shared memory {self.name} without permission")
            return None
            
        return self.memory.retrieve(memory_id)
        
    def search_by_tags(self, agent_id: str, tags: List[str], **kwargs) -> List[MemoryItem]:
        """Search memories by tags if agent has read access."""
        if not self.has_read_access(agent_id):
            logger.warning(f"Agent {agent_id} attempted to search shared memory {self.name} without permission")
            return []
            
        return self.memory.search_by_tags(tags, **kwargs)
        
    def search_by_context(self, agent_id: str, context: Dict[str, Any]) -> List[MemoryItem]:
        """Search memories by context if agent has read access."""
        if not self.has_read_access(agent_id):
            logger.warning(f"Agent {agent_id} attempted to search shared memory {self.name} without permission")
            return []
            
        return self.memory.search_by_context(context)
        
    def search_by_relevance(self, agent_id: str, query: str, **kwargs) -> List[Tuple[MemoryItem, float]]:
        """Search memories by relevance if agent has read access."""
        if not self.has_read_access(agent_id):
            logger.warning(f"Agent {agent_id} attempted to search shared memory {self.name} without permission")
            return []
            
        return self.memory.search_by_relevance(query, **kwargs)

class MemoryManager:
    """Central manager for shared memories and memory-related utilities."""
    
    def __init__(self):
        self.shared_memories = {}  # name -> SharedMemory
        
    def create_shared_memory(self, name: str, max_size: int = 10000) -> SharedMemory:
        """Create a new shared memory repository."""
        if name in self.shared_memories:
            raise ValueError(f"Shared memory '{name}' already exists")
            
        memory = SharedMemory(name, max_size)
        self.shared_memories[name] = memory
        return memory
        
    def get_shared_memory(self, name: str) -> Optional[SharedMemory]:
        """Get a shared memory repository by name."""
        return self.shared_memories.get(name)
        
    def list_shared_memories(self) -> List[str]:
        """List all shared memory repository names."""
        return list(self.shared_memories.keys())
