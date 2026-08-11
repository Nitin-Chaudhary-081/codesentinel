"""Tests for report generation."""

from datetime import datetime
import json
import pytest

from src.reports.generator import generate_markdown, generate_jsonl
from src.models import Evaluation, Submission, Language


@pytest.fixture
def sample_submission():
    return Submission(
        id=1,
        user_id=1,
        code="def hello(): return 'world'",
        language=Language.PYTHON,
        context=None,
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        updated_at=datetime(2025, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_evaluation():
    return Evaluation(
        id=1,
        submission_id=1,
        scores={
            "complexity": 8,
            "naming": 9,
            "error_handling": 5,
            "duplication": 9,
            "security": 8,
            "maintainability": 7,
        },
        feedback={
            "issues": ["Missing error handling"],
            "suggestions": ["Add type hints"],
            "highlights": ["Clean function naming"],
        },
        overall_score=7,
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )


def test_markdown_contains_scores(sample_evaluation, sample_submission):
    md = generate_markdown(sample_evaluation, sample_submission)
    assert "# Code Review Report" in md
    assert "**Overall Score:** 7/10" in md
    assert "Complexity" in md
    assert "python" in md


def test_markdown_contains_feedback(sample_evaluation, sample_submission):
    md = generate_markdown(sample_evaluation, sample_submission)
    assert "Missing error handling" in md
    assert "Add type hints" in md
    assert "Clean function naming" in md


def test_jsonl_valid_json(sample_evaluation, sample_submission):
    jsonl = generate_jsonl(sample_evaluation, sample_submission)
    record = json.loads(jsonl)
    assert record["id"] == 1
    assert record["language"] == "python"
    assert record["overall_score"] == 7
    assert "scores" in record
    assert "feedback" in record


def test_jsonl_contains_code(sample_evaluation, sample_submission):
    jsonl = generate_jsonl(sample_evaluation, sample_submission)
    record = json.loads(jsonl)
    assert "def hello()" in record["code"]
