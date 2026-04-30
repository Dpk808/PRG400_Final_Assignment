import json
import os

try:
    from openai import AzureOpenAI
except Exception:
    AzureOpenAI = None

_LAST_ERROR = ''

def _get_config() -> tuple[str, str, str, str]:
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', '').strip()
    key = os.environ.get('AZURE_OPENAI_KEY', '').strip()
    deployment = os.environ.get('AZURE_DEPLOYMENT', 'gpt-5-mini').strip()
    api_version = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-15-preview').strip()
    return endpoint, key, deployment, api_version

def sanitize_text(s: str) -> str:
    return ''.join(ch for ch in s if ord(ch) >= 32)


def build_prompt(survey_json: dict, library_sample: list) -> str:
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


def validate_config() -> tuple[bool, str]:
    if AzureOpenAI is None:
        return False, 'Python package "openai" is not installed.'
    endpoint, key, deployment, _api_version = _get_config()
    if not endpoint:
        return False, 'Missing AZURE_OPENAI_ENDPOINT.'
    if not key:
        return False, 'Missing AZURE_OPENAI_KEY.'
    if not deployment:
        return False, 'Missing AZURE_DEPLOYMENT.'
    return True, ''


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


def get_recommendations(survey_json: dict, library_sample: list, top_n: int = 5):
    global _LAST_ERROR
    ok, error = validate_config()
    if not ok:
        _LAST_ERROR = error
        return []

    endpoint, key, deployment, api_version = _get_config()

    prompt = build_prompt(survey_json, library_sample)
    _LAST_ERROR = ''

    try:
        client = AzureOpenAI(
            api_key=key,
            azure_endpoint=endpoint,
            api_version=api_version
        )

        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "Return only JSON. No prose."},
                {"role": "user", "content": prompt}
            ]
        )

        content = resp.choices[0].message.content or ''
        parsed = _extract_json_array(content)
        if isinstance(parsed, dict) and 'recommendations' in parsed:
            parsed = parsed.get('recommendations')
        if not isinstance(parsed, list):
            return []
        return _normalize_recommendations(parsed)[:top_n]
    except Exception as exc:
        _LAST_ERROR = f"Azure OpenAI error: {exc}"
        return []
