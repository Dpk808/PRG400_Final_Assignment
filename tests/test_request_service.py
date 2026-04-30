from services.request_service import RequestService
from library_app.extensions import db
from library_app.models import Book, BookRequest, User


def test_request_service_create(app):
    service = RequestService()
    with app.app_context():
        user = User.query.filter_by(username="student1").first()
        book = Book.query.first()
        record = service.create_request(user.id, book.id)
        assert isinstance(record, BookRequest)
        assert record.status == "pending"
        assert db.session.get(BookRequest, record.id) is not None
