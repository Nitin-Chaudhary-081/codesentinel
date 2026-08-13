"""Tests for the evaluation engine."""

import time

import pytest

from src.evaluation.engine import evaluate_code, _collect_function_types
from src.errors import CodeSyntaxError


class TestPythonEvaluation:
    def test_clean_code_scores_high(self):
        code = (
            "def calculate_total(items: list[float]) -> float:\n"
            "    return sum(items)\n"
        )
        scores, feedback = evaluate_code(code, "python")
        assert scores["complexity"] >= 7
        assert scores["naming"] >= 7

    def test_complex_code_scores_lower(self):
        code = (
            "def f(x):\n"
            "    if x == 1:\n"
            "        if x == 2:\n"
            "            if x == 3:\n"
            "                if x == 4:\n"
            "                    if x == 5:\n"
            "                        if x == 6:\n"
            "                            if x == 7:\n"
            "                                if x == 8:\n"
            "                                    if x == 9:\n"
            "                                        if x == 10:\n"
            "                                            return True\n"
            "    return False\n"
        )
        scores, feedback = evaluate_code(code, "python")
        assert scores["complexity"] <= 5
        assert len(feedback["issues"]) > 0

    def test_security_risk_detected(self):
        code = "result = eval(user_input)\n"
        scores, feedback = evaluate_code(code, "python")
        assert scores["security"] <= 5
        assert any("eval" in issue for issue in feedback["issues"])

    def test_error_handling_detected(self):
        code = (
            "def process(path):\n"
            "    try:\n"
            "        with open(path) as f:\n"
            "            return f.read()\n"
            "    except FileNotFoundError:\n"
            "        return ''\n"
        )
        scores, feedback = evaluate_code(code, "python")
        assert scores["error_handling"] >= 7

    def test_syntax_error_handled(self):
        code = "def broken(\n"
        with pytest.raises(CodeSyntaxError) as exc_info:
            evaluate_code(code, "python")
        assert exc_info.value.error_type == "syntax_error"
        assert exc_info.value.details.get("line") == 1


class TestTypeScriptEvaluation:
    def test_clean_code(self):
        code = (
            "function add(a: number, b: number): number {\n"
            "  return a + b;\n"
            "}\n"
        )
        scores, feedback = evaluate_code(code, "typescript")
        assert scores["complexity"] >= 7

    def test_security_risk(self):
        code = "element.innerHTML = userInput;\n"
        scores, feedback = evaluate_code(code, "typescript")
        assert scores["security"] <= 5


class TestGoEvaluation:
    def test_error_handling_present(self):
        code = (
            "func ReadFile(path string) ([]byte, error) {\n"
            "    data, err := os.ReadFile(path)\n"
            "    if err != nil {\n"
            "        return nil, err\n"
            "    }\n"
            "    return data, nil\n"
            "}\n"
        )
        scores, feedback = evaluate_code(code, "go")
        assert scores["error_handling"] >= 8

    def test_missing_error_handling(self):
        code = (
            "func ReadFile(path string) []byte {\n"
            "    data, _ := os.ReadFile(path)\n"
            "    return data\n"
            "}\n"
        )
        scores, feedback = evaluate_code(code, "go")
        assert scores["error_handling"] <= 5


class TestGenericEvaluation:
    def test_empty_code(self):
        scores, feedback = evaluate_code("", "python")
        assert all(1 <= v <= 10 for k, v in scores.items() if isinstance(v, int))

    def test_scores_in_valid_range(self):
        code = "x = 1\n" * 50
        scores, feedback = evaluate_code(code, "python")
        for key, val in scores.items():
            if isinstance(val, int):
                assert 1 <= val <= 10, f"{key}={val} out of range"


class TestRegexSafety:
    def test_collect_function_types_no_redos(self):
        """A long string of balanced parens with no '=>' must not cause
        catastrophic backtracking (CWE-1333)."""
        code = "const x = " + "()." * 100 + "z"
        start = time.time()
        _collect_function_types(code)
        elapsed = time.time() - start
        assert elapsed < 0.5, f"regex took {elapsed:.2f}s (possible ReDoS)"

    def test_collect_function_types_detects_types(self):
        code = (
            "function add(a: number, b: number): number { return a + b; }\n"
            "const greet = (name: string) => name;\n"
        )
        types = _collect_function_types(code)
        assert types.get("add") == ["number", "number"]
        assert types.get("greet") == ["string"]
