"""Evaluations blueprint — trigger and retrieve code evaluations."""

from flask import Blueprint, request, jsonify
from sqlalchemy import select

from src.database import get_db
from src.evaluation.engine import evaluate_code
from src.models import Evaluation, Submission, SubmissionStatus, User
from src.blueprints.submissions import get_current_user, submission_to_dict
from src.errors import AnalysisError, CodeSyntaxError, CodeTypeError, UnsupportedLanguageError

bp = Blueprint("evaluations", __name__)


def evaluation_to_dict(e):
    return {
        "id": e.id,
        "submission_id": e.submission_id,
        "scores": e.scores,
        "feedback": e.feedback,
        "overall_score": e.overall_score,
        "created_at": e.created_at.isoformat(),
    }


@bp.route("/<int:submission_id>", methods=["POST"])
def run_evaluation(submission_id: int):
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

        existing = db.query(Evaluation).filter(
            Evaluation.submission_id == submission.id
        ).first()
        if existing:
            return jsonify({
                "status": "ok",
                "data": {
                    **evaluation_to_dict(existing),
                    "language": submission.language.value,
                    "analysis_status": "ok",
                    "syntax_valid": True,
                    "message": "Analysis already completed",
                },
            })

        submission.status = SubmissionStatus.PROCESSING
        db.commit()

        try:
            scores, feedback = evaluate_code(submission.code, submission.language.value)
            overall = round(sum(scores.values()) / len(scores))

            evaluation = Evaluation(
                submission_id=submission.id,
                scores=scores,
                feedback=feedback,
                overall_score=overall,
            )
            db.add(evaluation)
            submission.status = SubmissionStatus.COMPLETED
            db.commit()
            db.refresh(evaluation)

            return jsonify({
                "status": "ok",
                "data": {
                    **evaluation_to_dict(evaluation),
                    "language": submission.language.value,
                    "analysis_status": "ok",
                    "syntax_valid": True,
                    "message": "Analysis completed successfully",
                },
            })

        except CodeSyntaxError as e:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            return jsonify({
                "status": "error",
                "error_type": e.error_type,
                "message": str(e),
                "details": e.details,
                "data": {
                    "language": submission.language.value,
                    "analysis_status": "syntax_error",
                    "syntax_valid": False,
                    "error": {
                        "error_type": "syntax_error",
                        "message": str(e),
                        "details": e.details,
                    },
                    "scores": None,
                    "suggestions": None,
                },
            }), 422

        except CodeTypeError as e:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            return jsonify({
                "status": "error",
                "error_type": e.error_type,
                "message": str(e),
                "details": e.details,
                "data": {
                    "language": submission.language.value,
                    "analysis_status": "type_error",
                    "syntax_valid": False,
                    "error": {
                        "error_type": "type_error",
                        "message": str(e),
                        "details": e.details,
                    },
                    "scores": None,
                    "suggestions": None,
                },
            }), 422

        except UnsupportedLanguageError as e:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            return jsonify({
                "status": "error",
                "error_type": e.error_type,
                "message": str(e),
                "details": e.details,
                "data": {
                    "language": submission.language.value,
                    "analysis_status": "unsupported_language",
                    "error": {
                        "error_type": "unsupported_language",
                        "message": str(e),
                        "details": e.details,
                    },
                    "scores": None,
                    "suggestions": None,
                },
            }), 400

        except Exception as e:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            return jsonify({
                "status": "error",
                "error_type": "analysis_failed",
                "message": f"Analysis failed: {str(e)}",
                "data": {
                    "language": submission.language.value,
                    "analysis_status": "analysis_failed",
                    "error": {
                        "error_type": "analysis_failed",
                        "message": str(e),
                    },
                    "scores": None,
                    "suggestions": None,
                },
            }), 500

    finally:
        db.close()


@bp.route("/<int:submission_id>", methods=["GET"])
def get_evaluation(submission_id: int):
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "error_type": "unauthorized", "message": "Missing or invalid token"}), 401

    db = get_db()
    try:
        evaluation = db.query(Evaluation).join(Submission).filter(
            Evaluation.submission_id == submission_id, Submission.user_id == user.id
        ).first()
        if not evaluation:
            return jsonify({"status": "error", "error_type": "not_found", "message": "Evaluation not found"}), 404
        return jsonify({
            "status": "ok",
            "data": evaluation_to_dict(evaluation),
        })
    finally:
        db.close()
