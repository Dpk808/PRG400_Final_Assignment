import json

from library_app.extensions import db
from library_app.models import SurveyResponse


class SurveyService:
    REQUIRED_FIELDS = [
        'genre_type',
        'frequency',
        'mood',
        'length',
        'series_pref',
        'age_group',
        'reading_goal'
    ]

    def parse_payload(self, payload):
        if not isinstance(payload, dict):
            return None, 'Invalid survey payload.'

        normalized = {}
        for key in self.REQUIRED_FIELDS:
            val = payload.get(key)
            if not val:
                return None, 'Please complete all required survey fields.'
            normalized[key] = val

        normalized['fiction_genres'] = payload.get('fiction_genres') or []
        normalized['nonfiction_genres'] = payload.get('nonfiction_genres') or []
        normalized['avoid_topics'] = payload.get('avoid_topics') or []

        last_books = payload.get('last_books') or []
        normalized['last_books'] = [str(item or '') for item in last_books][:3]

        normalized['favorite_author'] = payload.get('favorite_author') or ''
        normalized['additional_preferences'] = payload.get('additional_preferences') or ''
        return normalized, None

    def parse_form(self, form):
        payload = {key: form.get(key) for key in self.REQUIRED_FIELDS}
        payload['fiction_genres'] = form.getlist('fiction_genres')
        payload['nonfiction_genres'] = form.getlist('nonfiction_genres')
        payload['avoid_topics'] = form.getlist('avoid_topics')

        payload['last_books'] = [
            form.get('last_book_1') or '',
            form.get('last_book_2') or '',
            form.get('last_book_3') or ''
        ]
        if form.get('skip_last_three'):
            payload['last_books'] = []

        payload['favorite_author'] = form.get('favorite_author') or ''
        payload['additional_preferences'] = form.get('additional_preferences') or ''

        return self.parse_payload(payload)

    def save_response(self, user_id, payload):
        survey_json = json.dumps(payload)
        record = SurveyResponse(user_id=user_id, data=survey_json)
        try:
            db.session.add(record)
            db.session.commit()
            return record
        except Exception:
            db.session.rollback()
            raise

    def get_latest_survey(self, user_id):
        return SurveyResponse.query.filter_by(user_id=user_id).order_by(
            SurveyResponse.created_at.desc()
        ).first()

    def parse_survey_data(self, data):
        try:
            return json.loads(data), None
        except Exception:
            return None, 'Invalid survey data.'
