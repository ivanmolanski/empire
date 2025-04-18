# Bach Empire AI App

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
   uv pip install -r requirements.txt
   ```

2. Generate models from OpenAPI YAML (if needed):
   ```
   .venv/Scripts/datamodel-codegen.exe --input openapi.yaml --input-file-type openapi --output models.py --field-constraints --use-standard-collections --use-title-as-name
   ```

3. Run the API:
   ```
   uvicorn app.main:app --reload
   ```

4. Start the RQ worker (for background jobs):
   ```
   python worker.py
   ```

5. Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

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

Built with ❤️ by ivanmolanski and contributors.
