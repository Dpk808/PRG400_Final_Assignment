# Library Management System

A modular Flask application for library lending with a survey-driven recommendation flow and a REST API.

## Features
- Student and admin dashboards with session-based auth
- Survey flow that stores answers and generates recommendations
- REST API for books, requests, survey, and recommendations
- 12-factor configuration via environment variables
- Containerized with Docker and Docker Compose
- Unit and integration tests with pytest

## Architecture (High-Level)
- `library_app/` holds the Flask app factory, blueprints, and WSGI entrypoint
- `services/` encapsulates domain logic (SOLID-oriented)
- `utils/` isolates external model integrations
- `templates/` renders the web UI

Detailed design decisions and tradeoffs are documented in [docs/architecture.md](docs/architecture.md).

## Configuration
All configuration is driven by environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session secret | `dev-secret` |
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///library.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_SECONDS` | Recommendation rate limit | `3` |
| `RECOMMENDER_BACKEND` | `azure` or `ollama` | `azure` |
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint | none |
| `AZURE_OPENAI_KEY` | Azure key | none |
| `AZURE_DEPLOYMENT` | Azure deployment | `gpt-5-mini` |
| `AZURE_OPENAI_API_VERSION` | Azure API version | `2024-02-15-preview` |
| `OLLAMA_URL` | Ollama base URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model | `mistral:latest` |

## Local Development
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python app.py
```

The server runs at `http://localhost:5000`.

## REST API (Selected)
- `GET /api/health`
- `GET /api/books?available=true&limit=100`
- `GET /api/books/<id>`
- `POST /api/requests` (student)
- `GET /api/requests` (student)
- `POST /api/requests/<id>/approve` (admin)
- `POST /api/requests/<id>/reject` (admin)
- `POST /api/requests/<id>/return` (admin)
- `POST /api/survey` (student)
- `GET /api/recommendations` (student)

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

When running via Docker Compose, open `http://localhost:5003`.
The app uses the SQLite file at `instance/library.db` (mounted into the container).
For recommendations, Docker Compose loads Azure credentials from `.env` and uses `RECOMMENDER_BACKEND=azure`.

## Default Credentials (Seed Data)
- Admin: `admin` / `admin123`
- Student: `student1` / `pass123`
