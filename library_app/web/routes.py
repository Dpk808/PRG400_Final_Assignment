from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from library_app.extensions import db
from library_app.models import User
from utils.azure_openai import get_last_error, validate_config
from utils.ollama import get_last_error as get_ollama_last_error, ping_ollama


web_bp = Blueprint("web", __name__)


def _services():
    return current_app.extensions["services"]


def _normalize_username(raw: str | None) -> str:
    return (raw or "").strip().lower()


@web_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "student":
            return redirect(url_for("web.student_dashboard"))
        return redirect(url_for("web.admin_dashboard"))
    return redirect(url_for("web.login"))


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = _normalize_username(request.form.get("username"))
        password = request.form.get("password")
        user = User.query.filter(func.lower(User.username) == username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("web.index"))
        flash("Invalid username or password", "error")

    return render_template("login.html")


@web_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("web.index"))

    if request.method == "POST":
        username = _normalize_username(request.form.get("username"))
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("web.signup"))
        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return redirect(url_for("web.signup"))
        if " " in username:
            flash("Username cannot contain spaces.", "error")
            return redirect(url_for("web.signup"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("web.signup"))
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("web.signup"))

        if User.query.filter(func.lower(User.username) == username).first():
            flash("Username already exists. Try another one.", "error")
            return redirect(url_for("web.signup"))

        student = User(username=username, password=generate_password_hash(password), role="student")
        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists. Try another one.", "error")
            return redirect(url_for("web.signup"))
        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("web.login"))

    return render_template("signup.html")


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("web.login"))


@web_bp.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return redirect(url_for("web.index"))

    services = _services()
    requests_data = services["request_service"].get_user_requests(current_user.id)
    books_by_category = services["book_service"].get_available_books_grouped()
    active_requests_count = services["request_service"].count_active_requests(current_user.id)

    return render_template(
        "student_dashboard.html",
        requests=requests_data,
        books_by_category=books_by_category,
        active_requests_count=active_requests_count,
    )


@web_bp.route("/student/request-book/<int:book_id>", methods=["POST"])
@login_required
def request_book(book_id):
    if current_user.role != "student":
        return redirect(url_for("web.index"))

    services = _services()
    request_service = services["request_service"]
    book_service = services["book_service"]

    active_requests = request_service.count_open_requests(current_user.id)
    if active_requests >= 3:
        flash("You can only request maximum 3 books", "error")
        return redirect(url_for("web.student_dashboard"))

    if request_service.has_pending_request(current_user.id, book_id):
        flash("You have already requested this book", "warning")
        return redirect(url_for("web.student_dashboard"))

    book = book_service.get_book(book_id)
    if not book or book.available_count <= 0:
        flash("Book is not available", "error")
        return redirect(url_for("web.student_dashboard"))

    request_service.create_request(current_user.id, book_id)

    flash(f'Request for "{book.title}" submitted successfully!', "success")
    return redirect(url_for("web.student_dashboard"))


@web_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("web.index"))

    services = _services()
    pending_requests = services["request_service"].get_pending_requests()
    active_borrowings = services["request_service"].get_active_borrowings()
    books_by_category = services["book_service"].get_all_books_grouped()

    return render_template(
        "admin_dashboard.html",
        pending_requests=pending_requests,
        active_borrowings=active_borrowings,
        books_by_category=books_by_category,
    )


@web_bp.route("/admin/approve-request/<int:request_id>", methods=["POST"])
@login_required
def approve_request(request_id):
    if current_user.role != "admin":
        return redirect(url_for("web.index"))

    services = _services()
    book_request = services["request_service"].get_request(request_id)
    if not book_request:
        flash("Request not found", "error")
        return redirect(url_for("web.admin_dashboard"))

    if book_request.book.available_count <= 0:
        flash("Book is no longer available", "error")
        return redirect(url_for("web.admin_dashboard"))

    services["request_service"].approve_request(book_request, due_days=10)
    flash(f"Request approved for {book_request.user.username}", "success")
    return redirect(url_for("web.admin_dashboard"))


@web_bp.route("/admin/reject-request/<int:request_id>", methods=["POST"])
@login_required
def reject_request(request_id):
    if current_user.role != "admin":
        return redirect(url_for("web.index"))

    services = _services()
    book_request = services["request_service"].get_request(request_id)
    if not book_request:
        flash("Request not found", "error")
        return redirect(url_for("web.admin_dashboard"))

    requester_name = "student"
    try:
        requester_name = book_request.user.username
    except Exception:
        pass

    services["request_service"].reject_request(book_request)
    flash(f"Request rejected for {requester_name}", "warning")
    return redirect(url_for("web.admin_dashboard"))


@web_bp.route("/admin/return-book/<int:request_id>", methods=["POST"])
@login_required
def return_book(request_id):
    if current_user.role != "admin":
        return redirect(url_for("web.index"))

    services = _services()
    book_request = services["request_service"].get_request(request_id)
    if not book_request:
        flash("Request not found", "error")
        return redirect(url_for("web.admin_dashboard"))

    services["request_service"].return_book(book_request)
    flash(f"Book returned by {book_request.user.username}", "success")
    return redirect(url_for("web.admin_dashboard"))


@web_bp.route("/survey")
@login_required
def survey():
    return render_template("survey.html")


@web_bp.route("/survey/submit", methods=["POST"])
@login_required
def survey_submit():
    services = _services()
    payload, error = services["survey_service"].parse_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("web.survey"))

    try:
        services["survey_service"].save_response(current_user.id, payload)
    except Exception:
        flash("Failed to save survey. Try again.", "error")
        return redirect(url_for("web.survey"))

    flash("Thanks — your answers have been recorded. Recommendations coming soon.", "success")
    return redirect(url_for("web.recommendations"))


@web_bp.route("/recommendations")
@login_required
def recommendations():
    backend = current_app.config.get("RECOMMENDER_BACKEND", "azure")
    if backend == "ollama":
        ok, error = ping_ollama()
    else:
        ok, error = validate_config()
    if not ok:
        flash(error, "error")
        return redirect(url_for("web.survey"))

    services = _services()
    uid = current_user.id
    if not services["rate_limiter"].allow(uid):
        flash("Please wait a moment before requesting recommendations again.", "error")
        return redirect(url_for("web.student_dashboard"))

    survey = services["survey_service"].get_latest_survey(uid)
    if not survey:
        flash("No survey found. Please complete the survey first.", "error")
        return redirect(url_for("web.survey"))

    survey_data, error = services["survey_service"].parse_survey_data(survey.data)
    if error:
        flash(error, "error")
        return redirect(url_for("web.survey"))

    library_books = services["book_service"].get_library_sample(limit=20)
    suggestions = services["recommendation_service"].get_suggestions(
        survey_data,
        library_books,
        top_n=5,
    )
    if not suggestions:
        if backend == "ollama":
            err = get_ollama_last_error()
            msg = err or "Ollama did not return recommendations. Please try again."
        else:
            err = get_last_error()
            msg = err or "Azure OpenAI did not return recommendations. Please try again."
        flash(msg, "error")
        return redirect(url_for("web.survey"))

    matched = services["book_service"].match_suggestions(suggestions)
    return render_template("recommendations.html", recommendations=matched)
