import logging

from dotenv import load_dotenv
from flask import Flask
from werkzeug.security import generate_password_hash

from .config import Config
from .extensions import db, login_manager
from .models import User
from .api.routes import api_bp
from .web.routes import web_bp
from services.book_service import BookService
from services.request_service import RequestService
from services.survey_service import SurveyService
from services.recommendation_service import RecommendationService
from services.rate_limiter import InMemoryRateLimiter
from utils.azure_openai import get_recommendations, sanitize_text
from utils.ollama import get_recommendations as get_ollama_recommendations


def _configure_logging(app: Flask) -> None:
    level_name = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def _init_services(app: Flask) -> None:
    backend = app.config.get("RECOMMENDER_BACKEND", "azure")
    recommender = get_recommendations
    if backend == "ollama":
        recommender = get_ollama_recommendations

    services = {
        "book_service": BookService(),
        "request_service": RequestService(),
        "survey_service": SurveyService(),
        "recommendation_service": RecommendationService(recommender, sanitize_text),
        "rate_limiter": InMemoryRateLimiter(seconds=app.config["RATE_LIMIT_SECONDS"]),
    }
    app.extensions["services"] = services


def _maybe_init_db(app: Flask) -> None:
    if not app.config.get("INIT_DB", False):
        return

    with app.app_context():
        db.create_all()
        if User.query.first() is None:
            db.session.add_all(
                [
                    User(username="admin", password=generate_password_hash("admin123"), role="admin"),
                    User(username="student1", password=generate_password_hash("pass123"), role="student"),
                    User(username="student2", password=generate_password_hash("pass123"), role="student"),
                ]
            )
            db.session.commit()


def create_app(config_object: object | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(Config)
    if config_object is not None:
        app.config.from_object(config_object)

    _configure_logging(app)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "web.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    _maybe_init_db(app)
    _init_services(app)

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    return app
