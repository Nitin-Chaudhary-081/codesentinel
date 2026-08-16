"""Reports blueprint — export evaluation reports in multiple formats."""

from flask import Blueprint, request, jsonify, Response

from src.database import get_db
from src.models import Evaluation, Submission
from src.blueprints.submissions import get_current_user
from src.reports.generator import generate_jsonl, generate_markdown

bp = Blueprint("reports", __name__)


@bp.route("/<int:submission_id>/export", methods=["GET"])
def export_report(submission_id: int):
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "error_type": "unauthorized", "message": "Missing or invalid token"}), 401

    fmt = request.args.get("format", "markdown")

    db = get_db()
    try:
        row = db.query(Evaluation, Submission).join(Submission).filter(
            Evaluation.submission_id == submission_id, Submission.user_id == user.id
        ).first()
        if not row:
            return jsonify({"status": "error", "error_type": "not_found", "message": "Report not found"}), 404

        evaluation, submission = row

        if fmt == "jsonl":
            content = generate_jsonl(evaluation, submission)
            media_type = "application/x-jsonl"
            filename = f"report_{submission_id}.jsonl"
        else:
            content = generate_markdown(evaluation, submission)
            media_type = "text/markdown"
            filename = f"report_{submission_id}.md"

        return Response(
            content,
            mimetype=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    finally:
        db.close()
