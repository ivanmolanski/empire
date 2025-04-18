from fastapi import FastAPI
from fastapi.routing import APIRoute
from google.adk.tools.function_tool import FunctionTool
from typing import List
from app.main import app

# Utility to wrap all FastAPI endpoints as MCP tools
def get_fastapi_mcp_tools() -> List[FunctionTool]:
    tools = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            # Only wrap POST/GET endpoints with a name and summary
            if route.name and route.summary:
                # Create a FunctionTool for each endpoint
                async def endpoint_tool(*args, **kwargs):
                    # Use FastAPI's dependency injection to call the endpoint
                    return await route.endpoint(*args, **kwargs)
                tool = FunctionTool(endpoint_tool, name=route.name, description=route.summary)
                tools.append(tool)
    return tools
