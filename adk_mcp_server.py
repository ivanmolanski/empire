import asyncio
import json
import logging
import sys
import os
from dotenv import load_dotenv
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
from app.services.command_agent import command_agent
from app.services.pmo_agent import pmo_agent
from app.services.fastapi_mcp_tools import get_fastapi_mcp_tools
from app.config import settings
from app.utils.version_check import verify_compatibility

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'mcp_server.log'), mode='a')
    ]
)
logger = logging.getLogger("mcp-server")

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)

# Check ADK and MCP compatibility
try:
    is_compatible = verify_compatibility(exit_on_failure=False)
    if not is_compatible:
        logger.warning("Running with compatibility issues. Some features may not work correctly.")
except Exception as e:
    logger.error(f"Error during compatibility check: {str(e)}")
    logger.warning("Proceeding with startup, but system may be unstable.")

# Load environment variables (for agent credentials, etc.)
load_dotenv()

# Wrap CommandAgent and PMOAgent as FunctionTools
command_tool = FunctionTool(command_agent.run_async)
pmo_tool = FunctionTool(pmo_agent.run_async)

# Import all specialized agents to expose as tools
from app.services.analytics_agent import analytics_agent
from app.services.artifact_agent import artifact_agent
from app.services.autocoder_agent import AutoCoderAgent
from app.services.error_handler_agent import ErrorHandlerAgent
from app.services.human_in_loop_agent import HumanInLoopAgent
from app.services.llm_agent import llm_switch_agent
from app.services.memory_agent import MemoryAgent
from app.services.niche_agent import discovery_agent
from app.services.review_agent import ReviewAgent
from app.services.scraper_agent import ScraperAgent
from app.services.seo_agent import SEOAgent
from app.services.website_agent import website_agent

# Instantiate any class-based agents
error_handler_tool = FunctionTool(ErrorHandlerAgent(name="ErrorHandlerAgent").run_async)
human_in_loop_tool = FunctionTool(HumanInLoopAgent(name="HumanInLoopAgent").run_async)
memory_tool = FunctionTool(MemoryAgent(name="MemoryAgent").run_async)
review_tool = FunctionTool(ReviewAgent(name="ReviewAgent").run_async)
artifact_tool = FunctionTool(artifact_agent.run_async) if hasattr(artifact_agent, 'run_async') else None

# Add all agent tools to the exposed_tools list
exposed_tools = [
    command_tool,
    pmo_tool,
    FunctionTool(analytics_agent.run_async),
    artifact_tool,
    FunctionTool(AutoCoderAgent.run_async),
    error_handler_tool,
    human_in_loop_tool,
    FunctionTool(llm_switch_agent.run_async),
    memory_tool,
    FunctionTool(discovery_agent.run_async),
    review_tool,
    FunctionTool(ScraperAgent.run_async),
    FunctionTool(SEOAgent.run_async),
    FunctionTool(website_agent.run_async)
]
# Remove any None values (e.g., if artifact_tool is None)
exposed_tools = [tool for tool in exposed_tools if tool is not None]

# Add FastAPI endpoints as MCP tools
tools_from_fastapi = get_fastapi_mcp_tools()
exposed_tools.extend(tools_from_fastapi)

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
                result = await tool.run_async(args=arguments, tool_context=None)
                # Format result as JSON for MCP TextContent
                response_text = json.dumps(result, indent=2, default=str)
                logger.info(f"Tool {name} executed successfully")
                logger.debug(f"Tool {name} result: {response_text[:200]}..." if len(response_text) > 200 else response_text)
                return [mcp_types.TextContent(type="text", text=response_text)]
            except Exception as e:
                logger.error(f"Failed to execute tool '{name}': {str(e)}", exc_info=True)
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
        logger.error(f"Error running MCP server: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Launching Empire ADK MCP Server with all agents...")
    logger.info(f"Exposed tools: {', '.join([tool.name for tool in exposed_tools])}")
    
    try:
        # Run the server
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user.")
    except Exception as e:
        print(f"MCP Server encountered an error: {e}")
    finally:
        print("MCP Server process exiting.")
