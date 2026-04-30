from datetime import datetime, timedelta

from library_app.extensions import db
from library_app.models import BookRequest


class RequestService:
    def get_user_requests(self, user_id):
        return BookRequest.query.filter_by(user_id=user_id).all()

    def count_active_requests(self, user_id):
        return BookRequest.query.filter_by(user_id=user_id, status='approved').count()

    def count_open_requests(self, user_id):
        return BookRequest.query.filter(
            BookRequest.user_id == user_id,
            BookRequest.status.in_(['pending', 'approved'])
        ).count()

    def has_pending_request(self, user_id, book_id):
        return BookRequest.query.filter_by(
            user_id=user_id, book_id=book_id, status='pending'
        ).first() is not None

    def create_request(self, user_id, book_id):
        new_request = BookRequest(user_id=user_id, book_id=book_id)
        db.session.add(new_request)
        db.session.commit()
        return new_request

    def get_pending_requests(self):
        return BookRequest.query.filter_by(status='pending').all()

    def get_active_borrowings(self):
        return BookRequest.query.filter_by(status='approved').all()

    def get_request(self, request_id):
        return BookRequest.query.get(request_id)

    def approve_request(self, book_request, due_days=10):
        book_request.book.available_count -= 1
        book_request.status = 'approved'
        book_request.due_date = datetime.utcnow() + timedelta(days=due_days)
        db.session.commit()

    def reject_request(self, book_request):
        db.session.delete(book_request)
        db.session.commit()

    def return_book(self, book_request):
        book_request.book.available_count += 1
        book_request.status = 'returned'
        db.session.commit()
