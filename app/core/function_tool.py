from typing import Callable, Any, Optional
import inspect
import asyncio

class FunctionTool:
    def __init__(self, func: Callable, name: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__
        self.description = func.__doc__ or ""
        self.is_async = inspect.iscoroutinefunction(func)
        
    async def run_async(self, args: dict, tool_context: Any = None):
        if self.is_async:
            return await self.func(**args)
        else:
            return self.func(**args)
