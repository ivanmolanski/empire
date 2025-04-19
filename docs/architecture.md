# Empire Architecture Documentation

## System Overview

The Empire project is a sophisticated multi-agent system that orchestrates AI agents to work together in building websites, researching niches, and managing web applications. The system combines Google's Agent Development Kit (ADK) with a custom agent framework and FastAPI to provide a robust, extensible platform.

## Core Components

### 1. Agent Framework (`app/core`)

The central framework that manages agent interactions, workflows, and tools:

- **Agent** (`agent.py`): Base class for all agents with tool registration capabilities
- **Communication** (`communication.py`): Inter-agent messaging system
- **Memory** (`memory.py`): Persistent storage for agent knowledge and context
- **Role Negotiation** (`role_negotiation.py`): Dynamic role assignment and team formation
- **Orchestrator** (`orchestrator.py`): Manages complex workflows spanning multiple agents
- **Tools** (`tools.py`): Defines the tool execution interface for agents

The `Empire` class in `app/core/__init__.py` provides a centralized entry point to all framework components.

### 2. Specialized Agents (`app/services`)

Domain-specific agents that inherit from the base `Agent` class:

- **Website Agent**: Creates and manages websites
- **Niche Agent**: Conducts market research and niche discovery
- **LLM Agent**: Manages switching between LLM providers (OpenRouter/Gemini)
- **Analytics Agent**: Processes website metrics and analytics
- **Hosting Agent**: Deploys websites to hosting providers
- And many more specialized agents...

### 3. API Layer (`app/routes`)

FastAPI routes that expose agent functionality as REST endpoints:

- User authentication and management
- Website creation and management
- Niche discovery and research
- Analytics and reporting
- LLM provider switching
- And more...

### 4. Model Context Protocol Integration

The Empire system integrates with VS Code and other clients through the Model Context Protocol (MCP):

- **MCP Server** (`adk_mcp_server.py`): Exposes agent tools via the MCP protocol
- **FastAPI MCP Tools** (`app/services/fastapi_mcp_tools.py`): Wraps API endpoints as MCP tools

## Integration with Google ADK

The Empire project leverages Google's Agent Development Kit (ADK) for agent orchestration:

### Key ADK Components Used

1. **LlmAgent**: For LLM-powered decision making and reasoning
2. **FunctionTool**: For wrapping functions as tools callable by LLM agents
3. **Tool Conversion Utilities**: For bridging between ADK tools and MCP tools

### Multiple LLM Provider Strategy

Empire uses a dual-provider strategy for redundancy and performance:

1. **Primary LLM**: OpenRouter with `agentica-org/deepcoder-14b-preview:free` model
2. **Fallback LLM**: Google Gemini with `gemini-2.0-flash-thinking-exp-01-21` model

Environment variables control which models are used, with well-defined fallback behaviors.

## Data Flow

1. User interacts with the system via:
   - REST API endpoints
   - VS Code (via MCP protocol)
   - Command line tools

2. Requests flow into specialized agents through:
   - Direct API calls
   - MCP tool invocations
   - Inter-agent messaging

3. Agents collaborate through:
   - Message passing via `communication.py`
   - Shared memory via `memory.py` 
   - Workflow orchestration via `orchestrator.py`

4. Results are returned to the user through:
   - API responses
   - MCP responses
   - Generated artifacts (websites, reports, etc.)

## Configuration

System configuration is centralized in `app/config.py` using Pydantic Settings:

- **Database Connection**: SQLite/Postgres configuration
- **Authentication**: JWT settings and security parameters
- **LLM Providers**: API keys and model selection for OpenRouter and Gemini
- **Redis**: For messaging and caching
- **Hosting**: Settings for website deployment providers

## Deployment

The Empire system can be deployed as:

1. **Development Mode**: Local deployment with SQLite
2. **Production Mode**: Containerized deployment with PostgreSQL
3. **Serverless**: Deployed as cloud functions with distributed state

## Error Handling and Resilience

The system implements robust error handling through:

1. **Logging**: Structured logging throughout the codebase
2. **Fallback Mechanisms**: Automatic switching between LLM providers
3. **Structured Error Responses**: Consistent error reporting across components
4. **Exception Tracking**: Capturing and reporting exceptions

## Security Considerations

1. **API Authentication**: JWT-based authentication for API endpoints
2. **Route Protection**: Limited exposure of routes as MCP tools
3. **Environment Security**: Careful management of API keys and secrets
4. **Input Validation**: Pydantic models enforce strict validation

## Future Extensions

1. **Additional Hosting Providers**: Integration with more hosting platforms
2. **Enhanced Analytics**: More sophisticated website analytics
3. **Team Collaboration**: Multi-user collaborative workflows
4. **Custom Domain Management**: Automated domain registration and configuration
