Implementation Plan: Book Recommendation Chatbot (Ollama)

Goal
- Build a chatbot that recommends 5 books to students based on survey answers (survey_questions.md). Recommendations will be produced by an Ollama model and shown in the web UI.

Phases & Tasks

1) Plan & Mapping (this file)
- Read `survey_questions.md` and map each question to structured fields.
- Define a compact JSON schema for survey answers to send to the model.

2) Backend: survey collection and storage
- Add a POST endpoint `/survey/submit` that accepts survey answers and stores them in a `SurveyResponse` model (optional) or session.
- Validate required fields and normalize multi-select answers into lists.
- Store timestamp and `user_id` (if logged in).

3) Prompt engineering & model integration
- Design a minimal, deterministic prompt template for the Ollama model that:
  - Receives the survey JSON
  - Reads library inventory metadata (title, author, category, available_count, isbn) — pass a small sample or let the model ask to prefer in-library books
  - Avoids recommending books listed in `last 3 books` answers
  - Returns exactly 5 concise suggestions with: title, author, short reason (one sentence), and a confidence score (0-1)
- Implement server-side code to call Ollama (HTTP or local IPC depending on setup). Use an API wrapper function `get_recommendations(survey_json, top_n=5)`.
- Rate-limit and protect the model endpoint; sanitize inputs to avoid prompt injection.

4) Matching with local inventory
- After getting model suggestions, match titles against `Book` records in the database.
- If a model suggests books not in the library, try to map by author+title fuzzy-match; otherwise show them as external suggestions but allow the student to request similar in-library titles.

5) UI: survey flow and results
- Replace the simple `survey.html` with a multi-page or single-page survey UI matching `survey_questions.md` layout.
- After submit, present a `recommendations.html` view showing 5 recommendations, each with:
  - Title, author, short reason, availability (in-library / not available), `Request` button if available
- Allow student to save feedback (like/dislike) to improve future prompts.

6) Security, privacy, and UX
- Require login to submit survey; tie responses to `user_id`.
- Respect 'avoid' topics and age-group constraints in prompts.
- Avoid exposing raw model responses to end-users; sanitize before render.

7) Testing & QA
- Unit tests for: prompt builder, model wrapper (mocked), survey parsing, and DB mapping.
- Integration test: submit sample survey and verify 5 recommendations displayed.

8) Deployment & Ops
- Document how to run Ollama locally or remote (env vars). Add configuration in `README.md`.
- Add rate limits and caching for repeated queries.

Deliverables (incremental)
- `implementation_plan.md` (this file)
- Backend endpoint(s): `/survey` (GET), `/survey/submit` (POST), `/recommendations` (GET)
- `templates/survey.html` (improved), `templates/recommendations.html`
- `models.py` addition: `SurveyResponse` (optional)
- `utils/ollama.py` wrapper with an interface `get_recommendations()`
- Tests under `tests/` and updated `requirements.txt` if new deps are needed

Estimated timeline
- Plan & schema: 0.5 day
- Backend endpoints + DB model: 1 day
- Prompt engineering + Ollama wrapper: 1 day (iteration)
- UI and integration: 1 day
- Tests & polish: 0.5 day

Next immediate actions (I can do now)
- Implement the `SurveyResponse` model and POST endpoint to collect answers.
- Replace `survey.html` with a fuller form matching `survey_questions.md` and wire POST to `/survey/submit`.
- Add a stub `utils/ollama.py` that returns static 5-book suggestions (for local testing) and implement `recommendations.html` to show results.

Notes & Constraints
- Ollama setup: I need the user's Ollama host/connection details or to use a local model. We'll keep the code modular so the integration point is isolated.
- Keep prompts deterministic and enforce output format (JSON list of 5 suggestions) to simplify parsing.

Would you like me to start with the immediate actions (create DB model + POST endpoint + improved survey form)?