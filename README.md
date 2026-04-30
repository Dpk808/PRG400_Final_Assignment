# Project Requirements Evidence

This document maps the stated requirements to concrete places in the codebase.

## 1) SOLID, clean modular architecture
- App factory and configuration entrypoint: [library_app/__init__.py](library_app/__init__.py)
- Shared extensions (DB, login manager): [library_app/extensions.py](library_app/extensions.py)
- Web routes separated from API routes: [library_app/web/routes.py](library_app/web/routes.py) and [library_app/api/routes.py](library_app/api/routes.py)
- Domain logic split into services: [services](services)
- External integrations isolated: [utils](utils)
- Data models isolated: [library_app/models.py](library_app/models.py)

Why this addresses SOLID:
- Single Responsibility: routes focus on HTTP, services on domain logic, utils on external integrations.
- Open/Closed: recommendation backend is pluggable via `RECOMMENDER_BACKEND`.
- Dependency Inversion: routes call interfaces in services instead of coupling to persistence or providers directly.

## 2) 12-Factor App (configuration, logging, environment management)
Configuration
- All runtime config is read from environment variables in [library_app/config.py](library_app/config.py).
- Configuration values documented in [README.md](README.md).

Logging
- Structured logging configured once in the app factory: [library_app/__init__.py](library_app/__init__.py).
- Logging output goes to stdout, suitable for container logs.

Environment management
- `.env` support for local dev via `python-dotenv` in [library_app/__init__.py](library_app/__init__.py).
- Docker Compose sets environment variables for the container runtime: [docker-compose.yml](docker-compose.yml).

## 3) RESTful API backend (Flask)
- API routes and JSON responses: [library_app/api/routes.py](library_app/api/routes.py)
- Example endpoints: `/api/books`, `/api/requests`, `/api/survey`, `/api/recommendations`

## 4) Containerization (Docker + Compose)
- Dockerfile defines the runtime image: [Dockerfile](Dockerfile)
- Compose orchestration and env wiring: [docker-compose.yml](docker-compose.yml)

## 5) Unit and integration tests
- Pytest setup and fixtures: [tests/conftest.py](tests/conftest.py)
- Unit tests (services): [tests/test_request_service.py](tests/test_request_service.py), [tests/test_survey_service.py](tests/test_survey_service.py)
- Integration tests (API): [tests/test_api_books.py](tests/test_api_books.py), [tests/test_api_requests.py](tests/test_api_requests.py)

## 6) Architecture decisions and tradeoffs
- Decision record and tradeoffs: [docs/architecture.md](docs/architecture.md)

## Requirement checklist
- SOLID modular architecture: Done
- 12-Factor config/logging/env management: Done
- RESTful API backend (Flask): Done
- Docker + Docker Compose: Done
- Unit + integration tests: Done
- Architecture decisions and tradeoffs: Done
