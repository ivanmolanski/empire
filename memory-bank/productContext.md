# Product Context: Bach AI Control System

## Why This Project Exists
Bach AI is designed to empower users—especially entrepreneurs, marketers, and developers—to rapidly discover profitable niches, generate and deploy AI-powered websites, and orchestrate complex workflows using state-of-the-art agent technology. The project addresses the need for a unified, extensible platform that simplifies AI-driven business automation and digital product creation.

## Problems Solved
- Reduces complexity of multi-agent orchestration and AI integration.
- Eliminates manual setup for LLM switching, niche discovery, and website generation.
- Provides a seamless bridge between VS Code (Cline) and backend AI agents.
- Enables rapid prototyping and deployment of new digital businesses with minimal technical friction.
- Ensures maintainability and scalability by leveraging modern Python, ADK, and FastAPI best practices.

## How It Should Work
- Users interact via VS Code Insiders (Cline) or API endpoints.
- Commands are routed to specialized agents (niche discovery, website creation, etc.) coordinated by a Master Control Agent.
- LLM provider can be switched on demand (OpenRouter, Gemini) for cost and capability optimization.
- All workflows are modular, observable, and extensible for future features.

## User Experience Goals
- Zero-config onboarding for developers using VS Code and uv.
- Fast, reliable, and explainable agent actions with clear feedback.
- Intuitive command structure for Cline and API.
- Transparent status reporting and error handling.
- Easy extension for new agents, workflows, or integrations.
