"""Typed error types for CodeSentinel analysis."""


class AnalysisError(Exception):
    """Base error for code analysis."""
    def __init__(self, message: str, error_type: str, details: dict | None = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}


class CodeSyntaxError(AnalysisError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        details = {}
        if line is not None:
            details["line"] = line
        if column is not None:
            details["column"] = column
        super().__init__(message, "syntax_error", details)


class CodeTypeError(AnalysisError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None,
                 expected_type: str | None = None, actual_type: str | None = None):
        details = {}
        if line is not None:
            details["line"] = line
        if column is not None:
            details["column"] = column
        if expected_type is not None:
            details["expected_type"] = expected_type
        if actual_type is not None:
            details["actual_type"] = actual_type
        super().__init__(message, "type_error", details)


class UnsupportedLanguageError(AnalysisError):
    def __init__(self, language: str):
        super().__init__(
            f"Unsupported language: {language}",
            "unsupported_language",
            {"language": language, "supported": ["python", "typescript", "javascript", "go", "java", "cpp"]},
        )


class AnalysisFailedError(AnalysisError):
    def __init__(self, message: str):
        super().__init__(message, "analysis_failed")
