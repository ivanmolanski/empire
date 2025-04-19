#!/usr/bin/env python
"""
Simplified MCP server for Empire - integrates with Google ADK and exposes agent tools
"""
import asyncio
import json
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("mcp-server")

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'mcp_server.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info("Starting Empire MCP server...")

# Try importing required modules
try:
    # Import MCP modules
    from mcp import types as mcp_types
    from mcp.server.lowlevel import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    
    logger.info("Successfully imported MCP modules")
except ImportError as e:
    logger.error(f"Failed to import MCP modules: {str(e)}")
    logger.error("Please install MCP with: uv pip install mcp")
    sys.exit(1)

try:
    # Import Google ADK modules
    from google.adk.tools.function_tool import FunctionTool
    from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
    
    logger.info("Successfully imported Google ADK modules")
except ImportError as e:
    logger.error(f"Failed to import Google ADK modules: {str(e)}")
    logger.error("Please install Google ADK with: uv pip install google-adk")
    sys.exit(1)

# Import Empire modules
try:
    # Add the parent directory to the path so we can import app modules
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import core functionality
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    logger.info("Successfully imported basic dependencies")
    
    # Now try to import Empire-specific modules
    try:
        # Import agent modules - using a try/except for each to handle individual failures
        try:
            from app.services.command_agent import command_agent
            logger.info("Loaded command_agent")
            command_tool = FunctionTool(command_agent.run_async)
        except ImportError as e:
            logger.warning(f"Could not import command_agent: {str(e)}")
            command_tool = None
            
        try:
            from app.services.pmo_agent import pmo_agent
            logger.info("Loaded pmo_agent")
            pmo_tool = FunctionTool(pmo_agent.run_async)
        except ImportError as e:
            logger.warning(f"Could not import pmo_agent: {str(e)}")
            pmo_tool = None
            
        try:
            from app.services.llm_agent import llm_switch_agent
            logger.info("Loaded llm_switch_agent")
            llm_tool = FunctionTool(llm_switch_agent.run_async)
        except ImportError as e:
            logger.warning(f"Could not import llm_switch_agent: {str(e)}")
            llm_tool = None
            
        try:
            from app.services.website_agent import website_agent
            logger.info("Loaded website_agent")
            website_tool = FunctionTool(website_agent.run_async)
        except ImportError as e:
            logger.warning(f"Could not import website_agent: {str(e)}")
            website_tool = None
            
        try:
            from app.services.niche_agent import discovery_agent
            logger.info("Loaded discovery_agent")
            niche_tool = FunctionTool(discovery_agent.run_async)
        except ImportError as e:
            logger.warning(f"Could not import discovery_agent: {str(e)}")
            niche_tool = None
            
        try:
            from app.services.fastapi_mcp_tools import get_fastapi_mcp_tools
            logger.info("Loaded fastapi_mcp_tools")
            fastapi_tools = get_fastapi_mcp_tools()
        except ImportError as e:
            logger.warning(f"Could not import fastapi_mcp_tools: {str(e)}")
            fastapi_tools = []
            
    except Exception as e:
        logger.error(f"Error importing Empire modules: {str(e)}")
        logger.error("Starting with minimal functionality")
        command_tool = None
        pmo_tool = None
        llm_tool = None
        website_tool = None
        niche_tool = None
        fastapi_tools = []
        
except Exception as e:
    logger.error(f"Failed to load basic modules: {str(e)}")
    sys.exit(1)
    
# Create list of available tools
exposed_tools = []
for tool in [command_tool, pmo_tool, llm_tool, website_tool, niche_tool]:
    if tool is not None:
        exposed_tools.append(tool)

# Add FastAPI tools if available
if fastapi_tools:
    exposed_tools.extend(fastapi_tools)

# If no tools are available, create a simple test tool
if not exposed_tools:
    logger.warning("No agent tools found. Creating a test tool.")
    
    async def hello_world(name="world"):
        """Simple test function that returns a greeting"""
        return {"message": f"Hello, {name}!"}
    
    test_tool = FunctionTool(
        hello_world,
        name="hello_world",
        description="A test tool that returns a greeting"
    )
    exposed_tools.append(test_tool)

logger.info(f"Server loaded with {len(exposed_tools)} tools")
for tool in exposed_tools:
    logger.info(f"  - {tool.name}: {tool.description}")

# Create the server instance
server = Server(name="EmpireMCPServer")

@server.list_tools()
async def list_tools():
    """Advertise all ADK tools as MCP tools."""
    logger.info(f"Listing {len(exposed_tools)} available tools")
    mcp_tools = []
    for tool in exposed_tools:
        try:
            mcp_tool = adk_to_mcp_tool_type(tool)
            mcp_tools.append(mcp_tool)
        except Exception as e:
            logger.error(f"Error converting tool {tool.name} to MCP format: {str(e)}")
    
    return mcp_tools

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Route tool calls to the correct ADK FunctionTool."""
    logger.info(f"Tool call received: {name} with arguments: {json.dumps(arguments, default=str)}")
    
    for tool in exposed_tools:
        if name == tool.name:
            try:
                result = await tool.run_async(args=arguments)
                # Format result as JSON for MCP TextContent
                response_text = json.dumps(result, indent=2, default=str)
                logger.info(f"Tool {name} executed successfully")
                logger.debug(f"Tool {name} result: {response_text[:200]}..." if len(response_text) > 200 else response_text)
                return [mcp_types.TextContent(type="text", text=response_text)]
            except Exception as e:
                logger.error(f"Failed to execute tool '{name}': {str(e)}")
                error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
                return [mcp_types.TextContent(type="text", text=error_text)]
    
    # Tool not found
    logger.warning(f"Tool '{name}' not found")
    return [mcp_types.TextContent(type="text", text=f"Tool '{name}' not found.")]

async def run_server():
    """Run the MCP server using stdio communication"""
    logger.info("Starting MCP server using stdio communication")
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="Empire MCP Server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(notification_options=NotificationOptions()),
                ),
            )
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Launching Empire ADK MCP Server...")
    
    try:
        # Run the server
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
