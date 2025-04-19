"""
Communication protocols for inter-agent messaging and coordination.
"""
from typing import Any, Dict, List, Optional, Union, Callable
import asyncio
import uuid
from datetime import datetime
import logging
from pydantic import BaseModel, Field
from app.core.agent import AgentContext

logger = logging.getLogger(__name__)

class Message(BaseModel):
    """Message structure for agent communication."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    sender_id: str
    recipient_id: str
    message_type: str  # protocol, request, response, broadcast, etc.
    content: Dict[str, Any] = {}
    conversation_id: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CommunicationChannel:
    """Bidirectional communication channel between agents."""
    
    def __init__(self, agent_a, agent_b, channel_type="direct"):
        self.id = str(uuid.uuid4())
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.channel_type = channel_type
        self.message_history = []
        self._callbacks = {}
    
    def send_message(self, sender, recipient, message_type, content, **kwargs) -> str:
        """Send a message through this channel."""
        if sender not in [self.agent_a, self.agent_b]:
            raise ValueError("Sender must be one of the agents in this channel")
        if recipient not in [self.agent_a, self.agent_b]:
            raise ValueError("Recipient must be one of the agents in this channel")
        
        message = Message(
            sender_id=sender.agent_id,
            recipient_id=recipient.agent_id,
            message_type=message_type,
            content=content,
            **kwargs
        )
        self.message_history.append(message)
        
        # Trigger callbacks
        callbacks = self._callbacks.get(message_type, [])
        for callback in callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error in message callback: {str(e)}")
        
        return message.id
    
    def get_messages(self, limit=None, message_type=None) -> List[Message]:
        """Get messages from the channel, optionally filtered by type."""
        messages = self.message_history
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
            
        if limit is not None:
            messages = messages[-limit:]
            
        return messages
    
    def register_callback(self, message_type, callback):
        """Register a callback for a specific message type."""
        if message_type not in self._callbacks:
            self._callbacks[message_type] = []
        self._callbacks[message_type].append(callback)

class MessageBus:
    """Central message bus for multi-agent communication."""
    
    def __init__(self):
        self.channels = {}  # Channel ID -> Channel
        self.direct_channels = {}  # (agent_a_id, agent_b_id) -> Channel
        self.topic_channels = {}  # topic -> List[Agent]
        self.callbacks = {}  # topic -> List[Callable]
        self._message_log = []
    
    def get_or_create_channel(self, agent_a, agent_b, channel_type="direct"):
        """Get an existing channel or create a new one if it doesn't exist."""
        # Sort agent IDs to ensure consistent lookup
        agent_ids = sorted([agent_a.agent_id, agent_b.agent_id])
        key = (agent_ids[0], agent_ids[1])
        
        if key in self.direct_channels:
            return self.direct_channels[key]
            
        # Create new channel
        channel = CommunicationChannel(agent_a, agent_b, channel_type)
        self.channels[channel.id] = channel
        self.direct_channels[key] = channel
        return channel
    
    def subscribe(self, agent, topic):
        """Subscribe an agent to a topic."""
        if topic not in self.topic_channels:
            self.topic_channels[topic] = []
        
        if agent not in self.topic_channels[topic]:
            self.topic_channels[topic].append(agent)
    
    def unsubscribe(self, agent, topic):
        """Unsubscribe an agent from a topic."""
        if topic in self.topic_channels:
            if agent in self.topic_channels[topic]:
                self.topic_channels[topic].remove(agent)
    
    def publish(self, sender, topic, message_type, content, **kwargs) -> List[str]:
        """Publish a message to all subscribers of a topic."""
        if topic not in self.topic_channels:
            logger.warning(f"No subscribers for topic: {topic}")
            return []
            
        message_ids = []
        timestamp = datetime.now()
        
        for recipient in self.topic_channels[topic]:
            if recipient.agent_id == sender.agent_id:
                continue  # Skip sending to self
                
            channel = self.get_or_create_channel(sender, recipient)
            message_id = channel.send_message(
                sender,
                recipient,
                message_type,
                content,
                timestamp=timestamp,
                **kwargs
            )
            message_ids.append(message_id)
        
        # Trigger any callbacks registered for this topic
        if topic in self.callbacks:
            message = Message(
                sender_id=sender.agent_id,
                recipient_id=f"topic:{topic}",
                message_type=message_type,
                content=content,
                timestamp=timestamp,
                **kwargs
            )
            for callback in self.callbacks.get(topic, []):
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in topic callback: {str(e)}")
        
        return message_ids
    
    def register_topic_callback(self, topic, callback):
        """Register a callback to be triggered when messages are published to a topic."""
        if topic not in self.callbacks:
            self.callbacks[topic] = []
        self.callbacks[topic].append(callback)
    
    def get_all_channels(self):
        """Get all communication channels."""
        return list(self.channels.values())
    
    def get_channel_by_id(self, channel_id):
        """Get a communication channel by ID."""
        return self.channels.get(channel_id)
