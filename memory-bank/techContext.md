# Tech Context: Bach AI Control System

## Technologies Used
- **Python 3.12+**: Core language for all backend and agent logic.
- **Pydantic v2**: Data validation and schema generation (no legacy v1 code).
- **FastAPI**: API layer, OpenAPI 3.0 spec, and route stubs.
- **uv**: Dependency and virtual environment management.
- **Uvicorn**: ASGI server for FastAPI.
- **httpx**: Async HTTP client for API integrations.
- **Cline**: VS Code Insiders extension for agent command/control.
- **OpenRouter & Gemini**: Supported LLM providers, switchable at runtime.
- **pytrends, scrapy, beautifulsoup4**: Data collection and analysis for niche discovery.
- **scikit-learn, numpy, pandas**: Data processing and ML for monitoring/optimization.
- **boto3, google-cloud-storage**: Cloud storage and backup.
- **stripe, sendgrid, python-jose, cryptography**: Monetization, email, security.

## Development Setup
- All dependencies managed via pyproject.toml and uv.
- Virtual environment: `.venv` created with `uv venv .venv`.
- Activate with `source .venv/Scripts/activate` (Windows/Git Bash).
- Install dependencies: `uv pip install .`
- Run app: `uvicorn main:app --reload`
- **No fastapi-code-generator**: Handwritten modular FastAPI app structure, fully compatible with Pydantic v2.
- All secrets/configs via environment variables or config.json (never hardcoded).

## Technical Constraints
- Must run on Windows 11, Git Bash, and VS Code Insiders.
- No paid dependencies; all libraries must be open source or free tier.
- All LLM API keys and sensitive data handled securely (never in repo).
- Directory structure must support modular, maintainable FastAPI and agent-based workflows.
- All code and configs must be compatible with CI/CD and containerization.

## Dependencies & Tool Usage Patterns
- Use latest stable versions of all core libraries (see pyproject.toml/requirements.txt).
- Prefer async patterns for all I/O and agent operations.
- Use OpenAPI YAML as the single source of truth for API contracts.
- Modularize routers, models, and business logic for easy extension and testing.
- **No typed-ast or fastapi-code-generator required for Python 3.12+ and Pydantic v2.**
