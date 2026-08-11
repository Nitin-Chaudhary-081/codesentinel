"""Schema definitions using dataclasses (pydantic v1 incompatible with Python 3.14)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models import Language, SubmissionStatus


@dataclass
class UserCreate:
    email: str
    password: str


@dataclass
class UserResponse:
    id: int
    email: str
    created_at: datetime


@dataclass
class Token:
    access_token: str
    token_type: str = "bearer"


@dataclass
class SubmissionCreate:
    code: str
    language: Language
    context: Optional[str] = None


@dataclass
class SubmissionResponse:
    id: int
    user_id: int
    code: str
    language: Language
    context: Optional[str]
    status: SubmissionStatus
    created_at: datetime
    updated_at: datetime


@dataclass
class ScoreBreakdown:
    complexity: int
    naming: int
    error_handling: int
    duplication: int
    security: int
    maintainability: int


@dataclass
class EvaluationResponse:
    id: int
    submission_id: int
    scores: ScoreBreakdown
    feedback: Dict[str, Any]
    overall_score: int
    created_at: datetime
