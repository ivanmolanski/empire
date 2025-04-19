# Empire Multi-Agent Orchestration Framework

A sophisticated, production-grade AI multi-agent system that combines Google's Agent Development Kit (ADK), Pydantic models, FastAPI, and Model Context Protocol (MCP) for orchestrating powerful AI agents that build and manage websites, research niches, and optimize digital assets.

<div align="center">

![Empire Framework](https://img.shields.io/badge/Empire-Framework-blue)
![Google ADK](https://img.shields.io/badge/Powered%20by-Google%20ADK-4285F4)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)
![MCP](https://img.shields.io/badge/Model%20Context-Protocol-674EA7)

**[User Manual](docs/user_manual.md)** | 
**[System Architecture](docs/architecture.md)** | 
**[API Reference](http://localhost:8000/docs)** | 
**[Monitoring](http://localhost:8000/monitoring/dashboard)**

</div>

> "Empire represents a breakthrough in multi-agent AI system design, implementing a fractal command structure with emergent intelligence through dynamic collaboration."

## 🌟 Key Capabilities

Empire is a groundbreaking multi-agent orchestration framework that delivers:

### 🤖 Advanced Agent Architecture
- **Multi-Agent Collaboration**: Specialized agents (Website, Niche, Analytics, SEO, etc.) work together to solve complex tasks
- **Google ADK Integration**: Powered by Google's Agent Development Kit for advanced reasoning capabilities
- **Dynamic Role Negotiation**: Agents can form teams and negotiate roles for different tasks
- **Memory Management**: Persistent agent memory for contextual awareness across sessions

### 🧩 Powerful Integrations
- **Model Context Protocol (MCP)**: Seamless integration with VS Code and other MCP-compatible clients
- **Dual-Provider LLM Strategy**: Uses OpenRouter (primary) and Google Gemini (fallback) for redundancy and performance
- **FastAPI Endpoints**: Comprehensive API endpoints with automatic Pydantic model validation
- **Monitoring Dashboard**: Real-time system metrics and agent performance visualization

### 🔧 Enterprise-Grade Infrastructure
- **Type-Safe APIs**: OpenAPI-driven, with Pydantic v2 models auto-generated from YAML
- **Modular Architecture**: Well-structured components for maintenance and extensibility  
- **Automated Backup**: Git-based backup system for version control and disaster recovery
- **Comprehensive Testing**: End-to-end tests for agent interactions and system components
- **Deployment Ready**: Prepared for deployment to Google Cloud Run or other hosting providers

## 🚀 Quickstart

1. **Install dependencies using UV for optimal performance**:
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Configure environment variables** (copy .env.example to .env and fill in values):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Generate models from OpenAPI YAML** (if needed):
   ```bash
   .venv/Scripts/datamodel-codegen.exe --input openapi.yaml --input-file-type openapi --output app/models.py --field-constraints --use-standard-collections --use-title-as-name
   ```

4. **Start the API server**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Start the MCP Server** for VS Code integration:
   ```bash
   python tools/mcp_manager.py start
   ```

6. **Access the interactive API documentation**:
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Monitoring Dashboard: [http://localhost:8000/monitoring/dashboard](http://localhost:8000/monitoring/dashboard)

## Project Structure

```
empire/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── api.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── webhook.py
│   │   ├── analytics.py
│   │   ├── llm.py
│   │   ├── niche.py
│   │   └── website.py
│   ├── config.py
│   ├── db.py
│   ├── auth.py
│   └── services/
├── worker.py
├── .env
├── requirements.txt
├── openapi.yaml
└── README.md
```

## License

MIT

---

Built with 🇷🇺 ❤️ by ivanmolanski and contributors.
