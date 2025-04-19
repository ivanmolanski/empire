from fastapi import FastAPI
from fastapi.routing import APIRoute
from google.adk.tools.function_tool import FunctionTool
from typing import List, Set
from app.main import app
import logging

logger = logging.getLogger(__name__)

# Define safe route patterns that can be exposed to MCP agents
SAFE_ROUTE_PATTERNS = {
    "/llm/switch-provider",
    "/niche/discover",
    "/website/create",
    "/website/view",
    "/analytics/website"
}

# Utility to wrap only designated FastAPI endpoints as MCP tools
def get_fastapi_mcp_tools() -> List[FunctionTool]:
    tools = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            # Only wrap endpoints that match the safe patterns
            if route.path in SAFE_ROUTE_PATTERNS and route.name and route.summary:
                logger.info(f"Exposing route as MCP tool: {route.path}")
                
                # Create a closure to capture the current route
                def create_endpoint_tool(current_route=route):
                    async def endpoint_tool(*args, **kwargs):
                        try:
                            # Use FastAPI's dependency injection to call the endpoint
                            return await current_route.endpoint(*args, **kwargs)
                        except Exception as e:
                            logger.error(f"Error executing MCP tool for {current_route.path}: {str(e)}")
                            return {"error": str(e)}
                    
                    # Return the endpoint tool function with proper metadata
                    endpoint_tool.__name__ = current_route.name
                    return endpoint_tool
                
                # Create and add the tool
                tool = FunctionTool(
                    create_endpoint_tool(), 
                    name=route.name, 
                    description=route.summary
                )
                tools.append(tool)
            elif route.path not in SAFE_ROUTE_PATTERNS and route.name and route.summary:
                logger.debug(f"Route not exposed as MCP tool (not in safe list): {route.path}")
    
    return tools
