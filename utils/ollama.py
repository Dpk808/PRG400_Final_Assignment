import json
import logging
import os
try:
    import requests
except Exception:
    requests = None

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'mistral:latest')
_LAST_ERROR = ''
_logger = logging.getLogger(__name__)

def sanitize_text(s: str) -> str:
    return ''.join(ch for ch in s if ord(ch) >= 32)

def build_prompt(survey_json: dict, library_sample: list) -> str:
    # Deterministic instruction to return JSON array of 5 items
    instruction = {
        "instruction": (
            "You are a book recommender. Given the survey answers and a small sample of library inventory, "
            "return EXACTLY 5 recommendations as a JSON array. Each item must be an object with keys: title, author, "
            "reason (one short sentence), and confidence (a number between 0 and 1). Do not include any extra text."
        ),
        "survey": survey_json,
        "library_sample": library_sample
    }
    return json.dumps(instruction)


def ping_ollama() -> tuple[bool, str]:
    try:
        if requests is None:
            return False, 'Python package "requests" is not installed.'
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            return False, f"Ollama returned HTTP {resp.status_code}."
        data = resp.json()
        model_names = {m.get('name') for m in data.get('models', [])}
        if OLLAMA_MODEL not in model_names:
            return False, f"Ollama model not found: {OLLAMA_MODEL}. Run: ollama pull {OLLAMA_MODEL}"
        return True, ''
    except Exception as exc:
        return False, f"Ollama not reachable at {OLLAMA_URL}. {exc}"


def get_last_error() -> str:
    return _LAST_ERROR

def _extract_json_array(raw_text: str) -> list:
    try:
        return json.loads(raw_text)
    except Exception:
        pass

    start = raw_text.find('[')
    end = raw_text.rfind(']')
    if start == -1 or end == -1 or end <= start:
        return []

    try:
        return json.loads(raw_text[start:end + 1])
    except Exception:
        return []


def _normalize_recommendations(items: list) -> list:
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get('title')
        author = item.get('author')
        reason = item.get('reason')
        confidence = item.get('confidence')
        if not title or not author or not reason:
            continue
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.5
        normalized.append({
            'title': title,
            'author': author,
            'reason': reason,
            'confidence': confidence
        })
    return normalized


def call_ollama(prompt: str, model: str | None = None) -> list:
    # Try HTTP API; if unavailable, return an empty list
    try:
        if requests is None:
            return []

        resolved_model = model or OLLAMA_MODEL
        global _LAST_ERROR
        _LAST_ERROR = ''
        _logger.info("Calling Ollama model=%s url=%s", resolved_model, OLLAMA_URL)

        resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": resolved_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
                "num_predict": 400
            }
        }, timeout=20)
        if resp.status_code != 200:
            _LAST_ERROR = f"Ollama generate failed: HTTP {resp.status_code} - {resp.text[:400]}"
            _logger.warning(_LAST_ERROR)
            return []
        data = resp.json()
        # expect text in data['response']
        text = data.get('response') or data.get('text') or data.get('output') or ''
        _logger.info("Ollama responded, parsing recommendations")
        _logger.debug("Ollama raw response (first 300 chars): %s", text[:300])
        parsed = _extract_json_array(text)
        if isinstance(parsed, dict) and 'recommendations' in parsed:
            parsed = parsed.get('recommendations')
        if not isinstance(parsed, list):
            return []
        return _normalize_recommendations(parsed)
    except Exception as exc:
        _LAST_ERROR = f"Ollama error: {exc}"
        return []

def get_recommendations(survey_json: dict, library_sample: list, top_n: int = 5):
    # Build prompt and call Ollama; return empty list if unavailable
    prompt = build_prompt(survey_json, library_sample)
    results = call_ollama(prompt)
    if not results:
        return []
    return results[:top_n]
