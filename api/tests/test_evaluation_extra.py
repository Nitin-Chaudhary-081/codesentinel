"""Additional evaluation-engine coverage: non-Python analyzers, type errors,
brace mismatches, and the unsupported-language path."""

import pytest

from src.evaluation.engine import evaluate_code
from src.errors import CodeSyntaxError, CodeTypeError, UnsupportedLanguageError


class TestJavaScriptEvaluation:
    def test_clean_js(self):
        code = "function add(a, b) { return a + b; }\n"
        scores, _ = evaluate_code(code, "javascript")
        assert scores["complexity"] >= 7

    def test_js_security_risk(self):
        code = "document.body.innerHTML = userInput;\n"
        scores, feedback = evaluate_code(code, "javascript")
        assert scores["security"] <= 5


class TestJavaEvaluation:
    def test_class_naming_and_generics(self):
        code = "public class UserService { private List<String> items; }\n"
        scores, feedback = evaluate_code(code, "java")
        assert scores["naming"] >= 8
        assert scores["maintainability"] >= 7

    def test_java_try_catch(self):
        code = "class A { void f() { try { doWork(); } catch (Exception e) {} } }\n"
        scores, _ = evaluate_code(code, "java")
        assert scores["error_handling"] >= 7

    def test_java_unbalanced_braces(self):
        code = "class A { void f() {}\n"
        with pytest.raises(CodeSyntaxError):
            evaluate_code(code, "java")


class TestCppEvaluation:
    def test_smart_ptr_and_nullptr(self):
        code = (
            "#include <memory>\n"
            "void f() { std::unique_ptr<int> p(new int(5)); int* q = nullptr; }\n"
        )
        scores, feedback = evaluate_code(code, "cpp")
        assert scores["security"] >= 10
        assert scores["maintainability"] >= 10

    def test_cpp_unbalanced_braces(self):
        code = "void f() {\n"
        with pytest.raises(CodeSyntaxError):
            evaluate_code(code, "cpp")


class TestTypeScriptTypeErrors:
    def test_type_mismatch_raises(self):
        code = (
            "function add(a: number, b: number): number {\n"
            "    return a + b;\n"
            "}\n"
            "add('hello', 2);\n"
        )
        with pytest.raises(CodeTypeError) as exc:
            evaluate_code(code, "typescript")
        assert exc.value.error_type == "type_error"

    def test_matching_types_ok(self):
        code = (
            "function add(a: number, b: number): number {\n"
            "    return a + b;\n"
            "}\n"
            "add(1, 2);\n"
        )
        scores, _ = evaluate_code(code, "typescript")
        assert "complexity" in scores


class TestBraceMismatch:
    def test_ts_unbalanced_parens(self):
        code = "function f() { return (1 + 2; }\n"
        with pytest.raises(CodeSyntaxError):
            evaluate_code(code, "typescript")

    def test_go_unbalanced_braces(self):
        code = "func f() { println('x')\n"
        with pytest.raises(CodeSyntaxError):
            evaluate_code(code, "go")


class TestUnsupportedLanguage:
    def test_raises(self):
        with pytest.raises(UnsupportedLanguageError):
            evaluate_code("x = 1", "rust")

    def test_unknown_language_string(self):
        with pytest.raises(UnsupportedLanguageError):
            evaluate_code("x = 1", "cobol")


class TestScoreRange:
    def test_all_languages_return_valid_range(self):
        samples = {
            "python": "x = 1\n",
            "typescript": "const x = 1;\n",
            "javascript": "var x = 1;\n",
            "go": "package main\nfunc main() {}\n",
            "java": "class A {}\n",
            "cpp": "int main() { return 0; }\n",
        }
        for lang, code in samples.items():
            scores, _ = evaluate_code(code, lang)
            assert set(scores.keys()) == {
                "complexity",
                "naming",
                "error_handling",
                "duplication",
                "security",
                "maintainability",
            }
            for v in scores.values():
                assert 1 <= v <= 10
