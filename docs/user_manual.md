# Empire Multi-Agent Framework User Manual

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Installation and Setup](#installation-and-setup)
3. [Running the Components](#running-the-components)
4. [MCP Integration and Usage](#mcp-integration-and-usage)
5. [Agent Capabilities and Functions](#agent-capabilities-and-functions)
6. [API Endpoint Documentation](#api-endpoint-documentation)
7. [Development Workflows](#development-workflows)
8. [Troubleshooting](#troubleshooting)

<a name="system-architecture-overview"></a>
## 1. System Architecture Overview

### The Orchestral Multi-Agent Architecture

Empire's architecture represents a breakthrough in multi-agent AI system design, implementing a fractal command structure with emergent intelligence through dynamic collaboration. The framework features:

#### Fractal Command Structure

- **Base Layer**: Specialized agents (Niche, SEO, Website) handle atomic operations
- **Control Layer**: PMO Agent coordinates workflows using combinatorial logic
- **Meta Layer**: Command Agent evolves strategies through reinforcement learning
- **Oversight Layer**: Human-in-Loop Agent provides ethical constraints

#### Core Technical Foundations

- **Google Agent Development Kit (ADK)**: Empire leverages Google's cutting-edge ADK to power agent reasoning capabilities, function tools, and agent-to-agent communication.

- **Pydantic V2 Integration**: The system uses Pydantic V2 for robust data validation, schema generation, and serialization. All models are automatically generated from OpenAPI specifications to ensure type safety throughout the system.

- **FastAPI Code Generation**: API endpoints are derived from OpenAPI specifications using datamodel-codegen, creating a seamless connection between specification and implementation.

- **Model Context Protocol (MCP)**: Enables integration with external tools like VS Code, allowing agents to be invoked directly from your development environment.

### Architectural Components

#### Empire Framework Core (`app/core/`)

The central nervous system of the framework, providing:

- **Agent Base Class**: Defines the fundamental interface for all agents
- **Message Bus**: Facilitates inter-agent communication with guaranteed delivery
- **Memory Manager**: Enables persistent storage and retrieval of agent knowledge
- **Role Negotiation**: Handles dynamic team formation and role assignment
- **Orchestrator**: Manages complex workflows spanning multiple agents
- **Tools Executor**: Provides a unified interface for agent tool execution

#### Specialized Agents (`app/services/`)

Domain-specific agents inheriting from the base Agent class:

- **Command Agent**: Interprets high-level directives and orchestrates execution
- **PMO Agent**: Manages project-level coordination and resource allocation
- **LLM Agent**: Handles switching between LLM providers (OpenRouter/Gemini)
- **Website Agent**: Creates and manages websites from conception to deployment
- **Niche Agent**: Conducts market research and discovers profitable niches
- **Analytics Agent**: Processes metrics and generates insights
- **SEO Agent**: Optimizes content for search engines
- **Review Agent**: Assesses quality and provides improvement recommendations
- **Error Handler Agent**: Manages exceptions and generates recovery strategies
- **Memory Agent**: Maintains persistent knowledge across sessions
- **Artifact Agent**: Manages generated content and resources
- **Human-in-Loop Agent**: Facilitates human oversight and intervention

#### API Layer (`app/routes/`)

RESTful endpoints exposing agent functionality:

- **User Management**: Authentication and user operations
- **Project Management**: Project creation and coordination
- **Website Operations**: Website creation, editing, and management
- **Niche Discovery**: Market research and opportunity identification
- **Analytics Interface**: Metrics collection and analysis
- **LLM Provider Management**: Control of AI model selection

#### Monitoring & Infrastructure

- **Real-time Monitoring**: Dashboard for system metrics and agent performance
- **Automatic Backup**: Git-based version control integration
- **Hosting Management**: Deployment to various hosting providers
- **Comprehensive Testing**: End-to-end and component-level test suites

### Key Integration Points

The Empire Framework implements several advanced integration mechanisms:

1. **Dynamic Capability Manifest**: Automatically detects agent tools and maintains compatibility matrices
2. **Antifragile Workflow System**: Workflows that improve through stress and adapt to failures
3. **Neural Accountability Framework**: Cross-agent oversight with behavioral signatures and impact tracing
4. **Emergent Learning Protocols**: Knowledge sharing through pattern cross-pollination and predictive transfer

<a name="installation-and-setup"></a>
## 2. Installation and Setup

### Prerequisites

- **Python 3.10+**: The framework is built with modern Python features
- **UV Package Manager**: For efficient dependency management
- **Git**: For version control and automatic backup
- **Docker** (optional): For containerized deployment

### Environment Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/empire.git
   cd empire
   ```

2. **Create and Activate Virtual Environment using UV**:
   ```bash
   uv venv
   source .venv/Scripts/activate  # For Windows Git Bash
   # Or: .venv\Scripts\activate  # For Windows CMD
   ```

3. **Install Dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your configuration:
     ```
     # LLM API Keys
     OPENROUTER_API_KEY=your-openrouter-key
     GEMINI_API_KEY=your-gemini-key
     
     # LLM Model Names
     PRIMARY_LLM_MODEL=agentica-org/deepcoder-14b-preview:free
     FALLBACK_LLM_MODEL=gemini-2.0-flash-thinking-exp-01-21
     
     # Database Configuration
     DATABASE_URL=sqlite+aiosqlite:///./empire.db
     
     # Security
     SECRET_KEY=your-secret-key
     ```

### Initial Setup

1. **Generate Pydantic Models**:
   ```bash
   .venv/Scripts/datamodel-codegen.exe --input openapi.yaml --input-file-type openapi --output app/models.py --field-constraints --use-standard-collections --use-title-as-name
   ```

2. **Initialize the Database**:
   ```bash
   python -c "from app.db import init_db; init_db()"
   ```

3. **Configure MCP for VS Code Integration**:
   - Install the Cline or Copilot Chat extension in VS Code
   - Configure the MCP server settings as described in the MCP Integration section

<a name="running-the-components"></a>
## 3. Running the Components

### Starting the API Server

The FastAPI server provides the primary interface for interacting with the system:

```bash
uvicorn app.main:app --reload
```

This makes the API available at `http://localhost:8000`, with the following resources:
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Specification: `http://localhost:8000/openapi.json`
- Monitoring Dashboard: `http://localhost:8000/monitoring/dashboard`

### Starting the MCP Server

The Model Context Protocol server enables integration with VS Code and other clients:

```bash
python simple_mcp_server.py
```

Alternatively, use the management script for more control:

```bash
# Start the server
python tools/mcp_manager.py start

# Check status
python tools/mcp_manager.py status

# View logs
python tools/mcp_manager.py logs

# Stop the server
python tools/mcp_manager.py stop

# Restart the server
python tools/mcp_manager.py restart
```

### Running Background Tasks

Empire uses a worker process to handle background tasks:

```bash
python worker.py
```

### Automated Backup

Start the automatic backup system with:

```bash
# One-time backup
python tools/backup.py

# Continuous backup (every 30 minutes)
python tools/backup.py --schedule 30 --push
```

<a name="mcp-integration-and-usage"></a>
## 4. MCP Integration and Usage

### What is MCP?

The Model Context Protocol (MCP) is a standardized interface for AI-powered tools. Empire integrates with MCP to expose its agents and API endpoints as tools that can be used directly from VS Code or other MCP-compatible clients.

### Setting up MCP in VS Code

1. **Install Cline or Copilot Chat** extension in VS Code.

2. **Configure MCP Server Settings**:
   
   Create or edit the settings file at:
   `<User Folder>/AppData/Roaming/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
   
   Add the Empire MCP server configuration:
   ```json
   {
     "mcpServers": {
       "empire": {
         "command": "python",
         "args": [
           "c:/path/to/empire/simple_mcp_server.py"
         ],
         "env": {},
         "autoApprove": [
           "*"
         ]
       }
     }
   }
   ```

### Using MCP Tools

1. **List Available Tools**: In Cline or Copilot Chat, type:
   ```
   /tools
   ```

2. **Use Tools Directly**: You can invoke any tool with natural language, for example:
   ```
   Create a website about healthy recipes for vegans
   ```

3. **Tool Categories**:
   - **Agent Tools**: Direct access to specialized agents like website creation or niche discovery
   - **API Endpoints**: Access to API endpoints through the FastAPI MCP tools
   - **Utility Tools**: Helper functions for common operations

### Example MCP Workflows

1. **Website Creation Workflow**:
   ```
   1. Discover a profitable niche about sustainable gardening
   2. Create a website targeting that niche with eco-friendly gardening tips
   3. Generate SEO-optimized content for the website
   4. Deploy the website to our hosting provider
   ```

2. **Analytics Workflow**:
   ```
   1. Analyze the performance of my gardening website
   2. Identify the top-performing pages and content
   3. Generate recommendations for improvement
   ```

<a name="agent-capabilities-and-functions"></a>
## 5. Agent Capabilities and Functions

### Command Agent

The Command Agent serves as the central control point for the system:

- **Intent Recognition**: Interprets high-level user requests
- **Workflow Orchestration**: Coordinates complex multi-agent processes
- **Strategy Development**: Evolves approaches based on results and feedback
- **Resource Allocation**: Optimizes system resources for tasks

**Usage Example**:
```python
from app.services.command_agent import command_agent

response = await command_agent.run_async(
    "Create a website about healthy vegan recipes, research the niche first, 
     then develop content strategy, and finally deploy the site"
)
```

### PMO Agent

The Project Management Office Agent handles project-level coordination:

- **Task Scheduling**: Creates and manages task sequences
- **Dependency Management**: Handles inter-task dependencies
- **Progress Tracking**: Monitors and reports on task completion
- **Resource Balancing**: Optimizes allocation of system resources

**Usage Example**:
```python
from app.services.pmo_agent import pmo_agent

project = await pmo_agent.run_async({
    "project_name": "Health Blog Network",
    "tasks": [
        {"name": "Market Research", "duration": 2},
        {"name": "Website Creation", "duration": 5, "depends_on": ["Market Research"]},
        {"name": "Content Development", "duration": 7, "depends_on": ["Market Research"]}
    ]
})
```

### Website Agent

The Website Agent handles all aspects of website creation and management:

- **Website Design**: Creates site structure and visual design
- **Content Integration**: Organizes and integrates content
- **Technical Setup**: Configures hosting and technical elements
- **Optimization**: Ensures performance and user experience

**Usage Example**:
```python
from app.services.website_agent import website_agent

website = await website_agent.run_async({
    "domain": "healthyveganrecipes.com",
    "type": "blog",
    "theme": "clean and minimal",
    "content_focus": "Easy vegan recipes for beginners"
})
```

### Niche Agent

The Niche Agent conducts market research and identifies opportunities:

- **Keyword Research**: Identifies valuable search terms
- **Competitor Analysis**: Assesses existing market players
- **Trend Detection**: Spots emerging market trends
- **Opportunity Scoring**: Quantifies potential of niches

**Usage Example**:
```python
from app.services.niche_agent import discovery_agent

niche_report = await discovery_agent.run_async({
    "seed_topic": "sustainable gardening",
    "audience": "urban homeowners",
    "monetization": ["affiliate", "display ads", "digital products"],
    "competition_level": "medium"
})
```

### LLM Switch Agent

The LLM Switch Agent manages transitions between different language models:

- **Provider Management**: Handles switching between LLM providers
- **Fallback Orchestration**: Implements failover when primary model fails
- **Performance Optimization**: Selects optimal model for each task
- **Cost Management**: Balances performance against cost considerations

**Usage Example**:
```python
from app.services.llm_agent import llm_switch_agent

# Switch to OpenRouter
await llm_switch_agent.run_async({"provider": "openrouter"})

# Switch to Gemini
await llm_switch_agent.run_async({"provider": "gemini"})

# Generate content
response = await llm_switch_agent.generate_content(
    "Write a blog post about container gardening"
)
```

### SEO Agent

The SEO Agent optimizes content for search engines:

- **Keyword Optimization**: Improves content targeting
- **On-Page Analysis**: Assesses SEO factors
- **Content Recommendations**: Suggests improvements
- **Competitive Positioning**: Analyzes against competitors

**Usage Example**:
```python
from app.services.seo_agent import SEOAgent

seo_agent = SEOAgent()
seo_report = await seo_agent.run_async({
    "url": "https://example.com/vegan-recipes",
    "target_keywords": ["easy vegan recipes", "vegan meal prep", "quick vegan meals"],
    "competitor_urls": ["https://competitor1.com", "https://competitor2.com"]
})
```

### Analytics Agent

The Analytics Agent processes and analyzes website metrics:

- **Performance Tracking**: Monitors key metrics
- **Insight Generation**: Identifies patterns and opportunities
- **Recommendation Creation**: Suggests improvements
- **Anomaly Detection**: Identifies unexpected patterns

**Usage Example**:
```python
from app.services.analytics_agent import analytics_agent

analytics_report = await analytics_agent.run_async({
    "website": "healthyveganrecipes.com",
    "date_range": {"start": "2025-03-01", "end": "2025-04-01"},
    "metrics": ["pageviews", "bounce_rate", "conversion_rate", "average_time_on_page"]
})
```

<a name="api-endpoint-documentation"></a>
## 6. API Endpoint Documentation

The Empire API is organized into logical modules with consistent pattern:

### LLM Endpoints

**Switch Provider**:
- **Path**: `/llm/switch-provider`
- **Method**: POST
- **Request Body**: 
  ```json
  {
    "provider": "openrouter" // or "gemini"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Switched to openrouter"
  }
  ```

### Niche Endpoints

**Discover Niche**:
- **Path**: `/niche/discover`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "niche": "vegan cooking",
    "keywords": ["vegan recipes", "plant-based meals"],
    "target_audience": "health-conscious millennials",
    "budget": 500.00,
    "duration": 30
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "niche_score": 82,
      "competition_level": "medium",
      "estimated_traffic": 15000,
      "recommended_keywords": [
        {"keyword": "easy vegan recipes", "volume": 8100, "difficulty": 40},
        {"keyword": "vegan meal prep", "volume": 6200, "difficulty": 35}
      ],
      "content_recommendations": [...]
    }
  }
  ```

**Daily Niche Report**:
- **Path**: `/niche/daily-report`
- **Method**: GET
- **Query Parameters**: `date=2025-04-18&niche=vegan-cooking`
- **Response**:
  ```json
  {
    "date": "2025-04-18",
    "niche": "vegan-cooking",
    "performance": {
      "traffic_trend": "+5.2%",
      "competition_change": "-1.3%",
      "new_opportunities": [...],
      "recommendations": [...]
    }
  }
  ```

### Website Endpoints

**Create Website**:
- **Path**: `/website/create`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "domain": "healthyveganrecipes.com",
    "content": "A website focused on quick, easy vegan recipes for busy professionals.",
    "design": "Minimalist with focus on food photography",
    "budget": 800.00,
    "deadline": "2025-05-15"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "website_url": "https://healthyveganrecipes.com",
    "admin_panel": "https://healthyveganrecipes.com/admin",
    "deployment_details": {...}
  }
  ```

**View Website**:
- **Path**: `/website/view`
- **Method**: GET
- **Query Parameters**: `domain=healthyveganrecipes.com`
- **Response**:
  ```json
  {
    "domain": "healthyveganrecipes.com",
    "content": {...},
    "design": {...},
    "analytics_summary": {...}
  }
  ```

### Analytics Endpoints

**Website Analytics**:
- **Path**: `/analytics/website`
- **Method**: GET
- **Query Parameters**: `website_id=healthyveganrecipes.com&period=30d`
- **Response**:
  ```json
  {
    "website_id": "healthyveganrecipes.com",
    "period": "30d",
    "metrics": {
      "total_visits": 24350,
      "unique_visitors": 18200,
      "page_views": 67500,
      "bounce_rate": 42.3,
      "avg_session_duration": 185,
      "top_pages": [...]
    }
  }
  ```

### Authentication and User Endpoints

**Authentication**:
- **Path**: `/auth/token`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "username": "user@example.com",
    "password": "secure_password"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJ0eXAi...",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```

**User Profile**:
- **Path**: `/users/me`
- **Method**: GET
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
  ```json
  {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "projects": [...],
    "settings": {...}
  }
  ```

<a name="development-workflows"></a>
## 7. Development Workflows

### Updating API Models from OpenAPI

Empire uses a code generation approach to maintain perfect alignment between API specifications and implementation:

1. **Edit the OpenAPI Specification**:
   
   Modify `openapi.yaml` to add or update endpoints and models.

2. **Generate Pydantic Models**:
   ```bash
   .venv/Scripts/datamodel-codegen.exe --input openapi.yaml --input-file-type openapi --output app/models.py --field-constraints --use-standard-collections --use-title-as-name
   ```

3. **Implement Route Logic**:
   
   Create or update route handlers in the appropriate file in `app/routes/`.

### Adding a New Agent

To add a new specialized agent to the system:

1. **Create Agent File**:
   
   Create a new file in `app/services/` (e.g., `app/services/translation_agent.py`).

2. **Implement Agent Class**:
   ```python
   from google.adk.agents import Agent
   
   class TranslationAgent(Agent):
       def __init__(self, name="TranslationAgent"):
           super().__init__(name=name)
           
       async def run_async(self, input_data):
           """Main entry point for the translation agent"""
           # Agent logic here
           return {"translated_text": "..."}
       
   # Create an instance
   translation_agent = TranslationAgent()
   ```

3. **Add to MCP Server**:
   
   Update `simple_mcp_server.py` to import and expose your new agent:
   
   ```python
   try:
       from app.services.translation_agent import translation_agent
       logger.info("Loaded translation_agent")
       translation_tool = FunctionTool(translation_agent.run_async)
   except ImportError as e:
       logger.warning(f"Could not import translation_agent: {str(e)}")
       translation_tool = None
   ```
   
   Add to the exposed tools list:
   ```python
   # Create list of available tools
   exposed_tools = []
   for tool in [command_tool, pmo_tool, llm_tool, website_tool, niche_tool, translation_tool]:
       if tool is not None:
           exposed_tools.append(tool)
   ```

4. **Create API Endpoint** (optional):
   
   Add a new route file or update an existing one to expose your agent via API:
   ```python
   from fastapi import APIRouter
   from app.models import TranslationRequest, TranslationResponse
   from app.services.translation_agent import translation_agent
   
   router = APIRouter()
   
   @router.post("/translate", response_model=TranslationResponse)
   async def translate_text(request: TranslationRequest):
       result = await translation_agent.run_async(request.dict())
       return TranslationResponse(**result)
   ```

### Running Tests

Empire includes comprehensive testing to ensure reliability:

1. **LLM Provider Switch Tests**:
   ```bash
   python tools/test_llm_switching.py
   ```

2. **End-to-End System Tests**:
   ```bash
   python tools/test_e2e.py
   ```

3. **Selected Test Categories**:
   ```bash
   python tools/test_e2e.py --test website
   python tools/test_e2e.py --test agent
   ```

<a name="troubleshooting"></a>
## 8. Troubleshooting

### Common Issues and Solutions

#### MCP Server Won't Start

**Issue**: The MCP server fails to start with import errors.

**Solutions**:
1. Verify that all dependencies are installed:
   ```bash
   uv pip install google-adk mcp
   ```

2. Check the MCP server logs:
   ```bash
   python tools/mcp_manager.py logs
   ```

3. Try using the simplified MCP server instead:
   ```bash
   python simple_mcp_server.py
   ```

#### Missing Models Error

**Issue**: API endpoints report missing models or model field errors.

**Solutions**:
1. Regenerate models from OpenAPI specification:
   ```bash
   .venv/Scripts/datamodel-codegen.exe --input openapi.yaml --input-file-type openapi --output app/models.py --field-constraints --use-standard-collections --use-title-as-name
   ```

2. Check for inconsistencies between routes and models:
   ```bash
   # Look at model definition
   grep -r "YourModelName" app/models.py
   
   # Look at route usage
   grep -r "YourModelName" app/routes/
   ```

#### LLM Provider Switching Fails

**Issue**: Unable to switch between OpenRouter and Gemini.

**Solutions**:
1. Verify API keys in `.env`:
   ```
   OPENROUTER_API_KEY=your-key-here
   GEMINI_API_KEY=your-key-here
   ```

2. Run the LLM switching test:
   ```bash
   python tools/test_llm_switching.py
   ```

3. Check logs for detailed error messages:
   ```bash
   cat logs/empire.log | grep "LLM"
   ```

#### Agent Not Available in MCP

**Issue**: A specific agent isn't showing up in the MCP tools list.

**Solutions**:
1. Verify the agent is correctly imported in `simple_mcp_server.py`

2. Check if the agent has the required `run_async` method

3. Restart the MCP server:
   ```bash
   python tools/mcp_manager.py restart
   ```

4. Look for specific import errors in the logs:
   ```bash
   cat logs/mcp_server.log | grep "Could not import"
   ```

#### Database Connection Errors

**Issue**: Application reports database connection issues.

**Solutions**:
1. Verify DATABASE_URL in `.env`:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./empire.db
   ```

2. Try reinitializing the database:
   ```python
   python -c "from app.db import init_db; init_db()"
   ```

3. Check database file permissions and path

### Getting Help

If you encounter issues not covered here, try these resources:

1. **Check Log Files**:
   ```bash
   cat logs/empire.log
   cat logs/mcp_server.log
   ```

2. **Run Diagnostic Tests**:
   ```bash
   python tools/test_e2e.py
   ```

3. **Review the Empire GitHub Repository**:
   - Check for known issues
   - Review recent commits for changes
   - Consider filing a new issue

4. **Contact Support**:
   - File an issue on GitHub
   - Reach out to the Empire development team

---

© 2025 Empire Multi-Agent Framework. All rights reserved.
