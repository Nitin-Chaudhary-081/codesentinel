"""Submissions blueprint — create, list, retrieve code submissions."""

from flask import Blueprint, request, jsonify
from sqlalchemy import select

from src.database import get_db
from src.models import Language, Submission, SubmissionStatus, User
from src.auth import decode_token
from src.errors import UnsupportedLanguageError

bp = Blueprint("submissions", __name__)


def get_current_user() -> User | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None

    db = get_db()
    try:
        return db.query(User).filter(User.id == int(payload["sub"])).first()
    finally:
        db.close()


def parse_language(language_str: str) -> Language:
    """Convert string to Language enum, raising clear error if unsupported."""
    try:
        return Language(language_str.lower())
    except ValueError:
        raise UnsupportedLanguageError(language_str)


def submission_to_dict(s):
    return {
        "id": s.id,
        "user_id": s.user_id,
        "code": s.code,
        "language": s.language.value,
        "context": s.context,
        "status": s.status.value,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat(),
    }


@bp.route("", methods=["POST"])
def create_submission():
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "error_type": "unauthorized", "message": "Missing or invalid token"}), 401

    data = request.get_json()

    if not data.get("code"):
        return jsonify({"status": "error", "error_type": "validation_error", "message": "Code is required"}), 400

    try:
        language = parse_language(data.get("language", "python"))
    except UnsupportedLanguageError as e:
        return jsonify({
            "status": "error",
            "error_type": e.error_type,
            "message": str(e),
            "details": e.details,
        }), 400

    db = get_db()
    try:
        submission = Submission(
            user_id=user.id,
            code=data["code"],
            language=language,
            context=data.get("context"),
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return jsonify({
            "status": "ok",
            "data": submission_to_dict(submission),
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "error_type": "server_error", "message": str(e)}), 500
    finally:
        db.close()


@bp.route("", methods=["GET"])
def list_submissions():
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "error_type": "unauthorized", "message": "Missing or invalid token"}), 401

    db = get_db()
    try:
        items = db.query(Submission).filter(
            Submission.user_id == user.id
        ).order_by(Submission.created_at.desc()).all()
        return jsonify({
            "status": "ok",
            "data": [submission_to_dict(s) for s in items],
        })
    finally:
        db.close()


@bp.route("/<int:submission_id>", methods=["GET"])
def get_submission(submission_id: int):
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "error_type": "unauthorized", "message": "Missing or invalid token"}), 401

    db = get_db()
    try:
        submission = db.query(Submission).filter(
            Submission.id == submission_id, Submission.user_id == user.id
        ).first()
        if not submission:
            return jsonify({"status": "error", "error_type": "not_found", "message": "Submission not found"}), 404
        return jsonify({
            "status": "ok",
            "data": submission_to_dict(submission),
        })
    finally:
        db.close()
