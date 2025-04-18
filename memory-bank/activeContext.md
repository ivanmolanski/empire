# Active Context: Bach AI Control System

## Current Work Focus
- Migrating to a production-grade, modular FastAPI app structure under `app/` for maximum scalability and maintainability.
- Integrating async SQLite (SQLModel), Redis Queue (RQ), JWT authentication, and .env-based config.
- Ensuring all routes use Pydantic v2 models generated from OpenAPI YAML.
- Harmonizing all route files, imports, and router registration for best practices.
- Preparing for advanced Pydantic and FastAPI usage in the next phase.

## Recent Changes
- Created new core files: `app/config.py`, `app/db.py`, `app/auth.py`, `worker.py`, `.env`, `requirements.txt`, and updated `README.md`.
- Directory structure now supports modular routes, services, and background tasks.
- All route files are type-safe, use correct model imports, and are ready for business logic and DB integration.
- Project is ready for CI/CD, cloud, or local deployment.

## Next Steps
- Move/copy all route files and models into `app/routes/` and `app/models.py` as needed.
- Update all imports to use the new `app.` namespace.
- Register all routers in `app/routes/api.py`.
- Test the full stack with `uvicorn app.main:app --reload` and `python worker.py`.
- Begin advanced Pydantic and FastAPI integration (validation, OpenAPI, async DB, background jobs).

## Active Decisions & Considerations
- SQLite is used for local dev (easy, portable, async-ready).
- RQ (Redis Queue) is used for background jobs.
- All secrets and config are managed via `.env` and pydantic-settings.
- JWT authentication is scaffolded for secure endpoints.

## Important Patterns & Learnings
- Modular, scalable structure is critical for future growth.
- All code is harmonized for type safety, maintainability, and extensibility.
- Memory bank is updated after every major architectural or implementation change.
