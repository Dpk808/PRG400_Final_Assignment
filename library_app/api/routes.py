from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from library_app.models import Book
from utils.azure_openai import get_last_error, validate_config
from utils.ollama import get_last_error as get_ollama_last_error, ping_ollama


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _services():
    return current_app.extensions["services"]


def _serialize_book(book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "category": book.category,
        "available_count": book.available_count,
    }


def _json_error(message: str, status: int):
    return jsonify({"error": message}), status


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok"})

# class BookRoute:
#     def __init__(self):
#         self.book_service = BookService()  # Hard dependency
        
#     def list_books(self):
#         return self.book_service.get_available_books()
    
# @api_bp.get("/books")
# def list_books():
#     services = _services()
#     book_service = services["book_service"] 
#     return book_service.get_available_books()



@api_bp.get("/books")
def list_books():
    available = request.args.get("available", "").lower()
    limit = request.args.get("limit", type=int)

    query = Book.query
    if available in {"1", "true", "yes"}:
        query = query.filter(Book.available_count > 0)

    if limit:
        query = query.limit(min(limit, 200))

    books = query.all()
    return jsonify([_serialize_book(book) for book in books])


@api_bp.get("/books/<int:book_id>")
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return _json_error("Book not found", 404)
    return jsonify(_serialize_book(book))


@api_bp.get("/requests")
@login_required
def list_requests():
    services = _services()
    status = request.args.get("status")
    requests_data = services["request_service"].get_user_requests(current_user.id)
    if status:
        requests_data = [r for r in requests_data if r.status == status]

    return jsonify([
        {
            "id": r.id,
            "book_id": r.book_id,
            "status": r.status,
            "request_date": r.request_date.isoformat(),
            "due_date": r.due_date.isoformat() if r.due_date else None,
        }
        for r in requests_data
    ])


@api_bp.post("/requests")
@login_required
def create_request():
    if current_user.role != "student":
        return _json_error("Only students can request books", 403)

    payload = request.get_json(silent=True) or {}
    book_id = payload.get("book_id")
    if not book_id:
        return _json_error("book_id is required", 400)

    services = _services()
    request_service = services["request_service"]
    book_service = services["book_service"]

    if request_service.count_open_requests(current_user.id) >= 3:
        return _json_error("Request limit reached", 400)

    if request_service.has_pending_request(current_user.id, book_id):
        return _json_error("Request already exists", 400)

    book = book_service.get_book(book_id)
    if not book or book.available_count <= 0:
        return _json_error("Book is not available", 400)

    book_request = request_service.create_request(current_user.id, book_id)
    return jsonify({
        "id": book_request.id,
        "book_id": book_request.book_id,
        "status": book_request.status,
    }), 201


@api_bp.post("/requests/<int:request_id>/approve")
@login_required
def approve_request(request_id):
    if current_user.role != "admin":
        return _json_error("Only admins can approve requests", 403)

    services = _services()
    book_request = services["request_service"].get_request(request_id)
    if not book_request:
        return _json_error("Request not found", 404)

    if book_request.book.available_count <= 0:
        return _json_error("Book is no longer available", 400)

    services["request_service"].approve_request(book_request, due_days=10)
    return jsonify({"status": "approved"})


@api_bp.post("/requests/<int:request_id>/reject")
@login_required
def reject_request(request_id):
    if current_user.role != "admin":
        return _json_error("Only admins can reject requests", 403)

    services = _services()
    book_request = services["request_service"].get_request(request_id)
    if not book_request:
        return _json_error("Request not found", 404)

    services["request_service"].reject_request(book_request)
    return jsonify({"status": "rejected"})


@api_bp.post("/requests/<int:request_id>/return")
@login_required
def return_book(request_id):
    if current_user.role != "admin":
        return _json_error("Only admins can return books", 403)

    services = _services()
    book_request = services["request_service"].get_request(request_id)
    if not book_request:
        return _json_error("Request not found", 404)

    services["request_service"].return_book(book_request)
    return jsonify({"status": "returned"})


@api_bp.post("/survey")
@login_required
def submit_survey():
    services = _services()
    payload = request.get_json(silent=True)
    data, error = services["survey_service"].parse_payload(payload)
    if error:
        return _json_error(error, 400)

    try:
        services["survey_service"].save_response(current_user.id, data)
    except Exception:
        return _json_error("Failed to save survey", 500)

    return jsonify({"status": "saved"}), 201


@api_bp.get("/recommendations")
@login_required
def get_recommendations():
    backend = current_app.config.get("RECOMMENDER_BACKEND", "azure")
    if backend == "ollama":
        ok, error = ping_ollama()
    else:
        ok, error = validate_config()
    if not ok:
        return _json_error(error, 400)

    services = _services()
    uid = current_user.id
    if not services["rate_limiter"].allow(uid):
        return _json_error("Rate limit exceeded", 429)

    survey = services["survey_service"].get_latest_survey(uid)
    if not survey:
        return _json_error("No survey found", 404)

    survey_data, error = services["survey_service"].parse_survey_data(survey.data)
    if error:
        return _json_error(error, 400)

    library_books = services["book_service"].get_library_sample(limit=20)
    suggestions = services["recommendation_service"].get_suggestions(
        survey_data,
        library_books,
        top_n=5,
    )
    if not suggestions:
        if backend == "ollama":
            msg = get_ollama_last_error() or "No recommendations returned"
        else:
            msg = get_last_error() or "No recommendations returned"
        return _json_error(msg, 502)

    matched = services["book_service"].match_suggestions(suggestions)
    return jsonify(matched)
