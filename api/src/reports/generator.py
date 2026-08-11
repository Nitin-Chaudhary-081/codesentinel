"""Report generator — markdown and JSONL output formats."""

import json

from src.models import Evaluation, Submission


def generate_markdown(evaluation: Evaluation, submission: Submission) -> str:
    scores = evaluation.scores
    lines = [
        f"# Code Review Report — Submission #{submission.id}",
        "",
        f"**Language:** {submission.language.value}",
        f"**Overall Score:** {evaluation.overall_score}/10",
        f"**Date:** {evaluation.created_at.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Score Breakdown",
        "",
        f"| Category | Score |",
        f"|----------|-------|",
        f"| Complexity | {scores.get('complexity', 'N/A')}/10 |",
        f"| Naming | {scores.get('naming', 'N/A')}/10 |",
        f"| Error Handling | {scores.get('error_handling', 'N/A')}/10 |",
        f"| Duplication | {scores.get('duplication', 'N/A')}/10 |",
        f"| Security | {scores.get('security', 'N/A')}/10 |",
        f"| Maintainability | {scores.get('maintainability', 'N/A')}/10 |",
        "",
        "## Feedback",
        "",
    ]

    feedback = evaluation.feedback
    if feedback.get("issues"):
        lines.append("### Issues")
        for issue in feedback["issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    if feedback.get("suggestions"):
        lines.append("### Suggestions")
        for suggestion in feedback["suggestions"]:
            lines.append(f"- {suggestion}")
        lines.append("")

    if feedback.get("highlights"):
        lines.append("### Highlights")
        for highlight in feedback["highlights"]:
            lines.append(f"- {highlight}")
        lines.append("")

    lines.append("## Submitted Code")
    lines.append(f"```{submission.language.value}")
    lines.append(submission.code)
    lines.append("```")

    return "\n".join(lines)


def generate_jsonl(evaluation: Evaluation, submission: Submission) -> str:
    record = {
        "id": submission.id,
        "language": submission.language.value,
        "code": submission.code,
        "context": submission.context,
        "scores": evaluation.scores,
        "overall_score": evaluation.overall_score,
        "feedback": evaluation.feedback,
        "created_at": evaluation.created_at.isoformat(),
    }
    return json.dumps(record, ensure_ascii=False)
