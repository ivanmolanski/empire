# Active Context: Bach AI Control System

## Current Work Focus
- Transitioning to a full, beginner-friendly scaffold using Google ADK (Agent Development Kit) concepts.
- Ensuring all terminology and architecture are approachable for newcomers, but robust for bold experimentation.
- Using datamodel-code-generator for Pydantic v2 model generation from OpenAPI YAML.
- Maintaining a modular FastAPI app structure for easy extension and learning.

## Recent Changes
- Fixed all TOML and dependency issues; project now installs cleanly with uv and pip.
- Modular FastAPI routes scaffolded and ready for further expansion.
- pyproject.toml now uses only modern, compatible dependencies (no typed-ast, no fastapi-code-generator).

## Next Steps
- Generate Pydantic v2 models from OpenAPI YAML (if not already done).
- Scaffold FastAPI endpoints using generated models for request/response validation.
- Provide clear, beginner-friendly explanations for all major concepts (ADK, Pydantic, FastAPI, OpenAPI, etc.).
- Optionally, introduce Google ADK agent patterns in a way that is easy to extend.

## Active Decisions & Considerations
- All code and documentation will be written with beginners in mind, but will not shy away from advanced features.
- Memory bank will be updated after every major architectural or implementation change.
- Focus on clarity, modularity, and hands-on learning.

## Important Patterns & Learnings
- datamodel-code-generator is the best tool for generating Pydantic v2 models from OpenAPI YAML.
- FastAPI is used for API routing and business logic, leveraging the generated models.
- Google ADK agent patterns can be layered on top for advanced orchestration, but are not required for a working API.
