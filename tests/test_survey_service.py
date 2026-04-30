from services.survey_service import SurveyService


def test_parse_payload_success():
    service = SurveyService()
    payload = {
        "genre_type": "Fiction",
        "frequency": "Every day",
        "mood": "Light",
        "length": "Short",
        "series_pref": "Series",
        "age_group": "18-25",
        "reading_goal": "Entertainment",
        "fiction_genres": ["Fantasy"],
        "nonfiction_genres": [],
        "avoid_topics": ["Politics"],
        "last_books": ["Book A", "Book B"],
        "favorite_author": "Jane Doe",
        "additional_preferences": "None",
    }
    normalized, error = service.parse_payload(payload)
    assert error is None
    assert normalized["genre_type"] == "Fiction"
    assert normalized["last_books"] == ["Book A", "Book B"]


def test_parse_payload_missing_fields():
    service = SurveyService()
    normalized, error = service.parse_payload({"genre_type": "Fiction"})
    assert normalized is None
    assert error
