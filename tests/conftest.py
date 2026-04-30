import pytest
from werkzeug.security import generate_password_hash

from library_app import create_app
from library_app.extensions import db
from library_app.models import Book, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATE_LIMIT_SECONDS = 0
    RECOMMENDER_BACKEND = "azure"


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        student = User(
            username="student1",
            password=generate_password_hash("pass123"),
            role="student",
        )
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="979-1234567890",
            category="Novels",
            available_count=2,
        )
        db.session.add_all([admin, student, book])
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
