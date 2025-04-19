from typing import Any, Dict, Optional
import inspect
import asyncio
import logging

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for agent execution"""
        if inspect.iscoroutinefunction(self.run):
            return await self.run(input_data)
        return self.run(input_data)
        
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous implementation of agent logic"""
        raise NotImplementedError("Agents must implement run() method")
        
    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name})"
