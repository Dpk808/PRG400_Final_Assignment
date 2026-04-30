# Architecture Decisions and Tradeoffs

## Overview
The application is organized as a Flask app factory with two blueprints:
- `web` for HTML pages and session-based login
- `api` for JSON REST endpoints

Domain logic lives in `services/` and external integrations in `utils/` to keep the web layer thin.

## Key Decisions
1. **App factory + blueprints**
   - *Why*: Enables testing with isolated app instances and clean separation between web and API routes.
   - *Tradeoff*: Slightly more boilerplate and a small learning curve for new contributors.

2. **Service layer for domain logic**
   - *Why*: Keeps controllers small and aligns with SOLID (single responsibility, dependency inversion).
   - *Tradeoff*: Adds indirection; requires clear boundaries and consistent naming.

3. **Environment-driven configuration (12-Factor)**
   - *Why*: Makes runtime behavior explicit and portable across dev, test, and containers.
   - *Tradeoff*: Requires environment setup; defaults are provided for local use only.

4. **Session auth for web and API**
   - *Why*: Reuses existing login flow and avoids building a second auth system.
   - *Tradeoff*: API clients must handle cookies; token-based auth would be more flexible.

5. **SQLite for local and Docker**
   - *Why*: Zero-setup for demo environments.
   - *Tradeoff*: Not ideal for high concurrency; production should use Postgres or MySQL.

6. **Recommendation backends (Azure or Ollama)**
   - *Why*: Pluggable backend lets you switch providers using `RECOMMENDER_BACKEND`.
   - *Tradeoff*: Two validation paths and slightly more conditional logic in the handler.

## Quality Strategy
- Unit tests cover service validation and database operations.
- Integration tests cover API endpoints with the Flask test client.
- Logging is stdout-based and controlled by `LOG_LEVEL` for 12-factor alignment.
