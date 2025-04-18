# Project Brief: Bach AI Control System

## Objective
Design and implement a modular, production-grade AI control system for niche discovery, website generation, and multi-agent orchestration, leveraging the latest agent development frameworks (Google ADK), FastAPI, and Pydantic v2. The system must support seamless LLM switching (OpenRouter, Gemini), integrate with VS Code Insiders via Cline, and be deployable with modern Python tooling (uv, pyproject.toml).

## Core Requirements
- Preserve all original system functionality while simplifying setup using ADK and modern Python best practices.
- Modular, agent-based architecture: Master Control Agent, function-specific agents, workflow agents.
- Seamless LLM provider switching (OpenRouter, Gemini) via API and agent logic.
- Full VS Code Insiders integration using Cline and MCP server for command/control.
- OpenAPI 3.0-compliant API for all major operations (LLM switch, niche discovery, website management).
- No-cost, cutting-edge technology stack (latest versions, no paid dependencies).
- Robust, extensible directory structure for maintainability and future growth.
- Automated code generation and validation using FastAPI Code Generator and Pydantic v2.
- Clear documentation and memory bank for all architectural decisions and workflows.

## Deliverables
- Complete project scaffold with all required directories and files.
- Production-ready OpenAPI YAML spec for codegen and validation.
- FastAPI app with route stubs and Pydantic v2 models.
- Agent-based orchestration using ADK (Python).
- MCP server for Cline integration.
- pyproject.toml, README.md, .gitignore, and config.json.
- All code and documentation ready for VS Code workflow and CI/CD.

## Constraints
- No removal of existing functionality; only simplification and modernization.
- All secrets/configs handled securely (no hardcoded secrets).
- Must be compatible with Windows 11, Git Bash, and VS Code Insiders.
- All dependencies managed via uv and pyproject.toml.
