# Bach Empire AI

A modular, production-grade FastAPI system for scalable AI-powered niche discovery, website generation, analytics, and automation.

## Features

- OpenAPI-driven, type-safe API (Pydantic v2 models auto-generated from YAML)
- Modular route structure (llm, niche, website, user, project, task, webhook, analytics)
- Async-ready, background task tracking, and webhook/event support
- JWT authentication and user/project management
- SQLite (via SQLModel) and Redis Queue (RQ) integration
- .env-based configuration for secrets and deployment
- Ready for CI/CD, cloud, or local deployment

## Quickstart

1. Install dependencies:
   ```
   uv pip install .
   ```

2. Generate models from OpenAPI YAML (if needed):
   ```
   .venv/Scripts/datamodel-codegen.exe --input openapi.yaml --input-file-type openapi --output models.py --field-constraints --use-standard-collections --use-title-as-name
   ```

3. Run the API:
   ```
   uvicorn main:app --reload
   ```

4. Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

## Project Structure

```
empire/
├── main.py
├── models.py
├── openapi.yaml
├── routes/
│   ├── __init__.py
│   ├── api.py
│   ├── llm.py
│   ├── niche.py
│   ├── website.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── webhook.py
│   └── analytics.py
├── memory-bank/
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   └── progress.md
├── pyproject.toml
├── .gitignore
└── README.md
```

## License

MIT

---

Built with ❤️ by ivanmolanski and contributors.
