# System Patterns: Bach AI Control System

## Architecture Overview
- Modular, agent-based system using Google ADK (Agent Development Kit) for orchestration.
- Master Control Agent coordinates all specialized agents (niche discovery, website creation, monitoring, etc.).
- Workflow agents (sequential, parallel) manage complex, multi-step operations.
- FastAPI provides a unified OpenAPI 3.0-compliant API surface for all core operations.
- MCP server bridges Cline (VS Code) to backend agents for command/control.

## Key Technical Decisions
- Adopted ADK for agent management and workflow composition.
- LLM abstraction layer enables seamless switching between OpenRouter and Gemini.
- All schemas and API contracts defined in OpenAPI YAML, code-generated with FastAPI Code Generator and Pydantic v2.
- All configuration and secrets handled via environment variables and config.json (no hardcoded secrets).
- Directory structure supports both agent-centric (ADK) and API-centric (FastAPI) workflows.

## Design Patterns
- **Master-Agent Pattern:** Central agent delegates to specialized sub-agents.
- **Workflow Pattern:** SequentialAgent and ParallelAgent for deterministic and concurrent flows.
- **Adapter Pattern:** LLMConfigAgent abstracts LLM provider details for downstream agents.
- **MCP Integration:** Command routing and status reporting via a message control protocol server.

## Component Relationships
- MasterControlAgent <-> Specialized Agents (niche, website, promotion, monitoring, security)
- LLMConfigAgent <-> All LLM-dependent agents
- FastAPI <-> All business logic via route stubs and models
- MCP Server <-> Cline (VS Code) <-> MasterControlAgent

## Critical Implementation Paths
- LLM switching and propagation to all dependent agents.
- Workflow agent composition for multi-step processes (e.g., niche discovery + website creation).
- API endpoint mapping to agent actions.
- Secure, observable, and extensible agent orchestration.
