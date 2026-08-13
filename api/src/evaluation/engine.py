"""Code evaluation engine — multi-language static analysis with realistic scoring."""

import ast
import re
from collections import Counter

from src.errors import CodeSyntaxError, CodeTypeError, UnsupportedLanguageError


def evaluate_code(code: str, language: str) -> tuple[dict[str, int], dict]:
    """Evaluate code and return (scores_dict, feedback_dict).

    Raises:
        CodeSyntaxError: If code has syntax errors
        CodeTypeError: If code has type errors (TypeScript)
        UnsupportedLanguageError: If language is not supported
    """
    analyzers = {
        "python": _analyze_python,
        "typescript": _analyze_typescript_javascript,
        "javascript": _analyze_typescript_javascript,
        "go": _analyze_go,
        "java": _analyze_java,
        "cpp": _analyze_cpp,
    }

    analyzer = analyzers.get(language)
    if analyzer is None:
        raise UnsupportedLanguageError(language)

    return analyzer(code)


def _find_line_for_brace_mismatch(code: str, char_open: str, char_close: str) -> int:
    """Find the line number where brace/paren mismatch occurs."""
    lines = code.split("\n")
    depth = 0
    for i, line in enumerate(lines, 1):
        for ch in line:
            if ch == char_open:
                depth += 1
            elif ch == char_close:
                depth -= 1
            if depth < 0:
                return i
    if depth > 0:
        return len(lines)
    return 1


def _collect_function_types(code: str) -> dict[str, list[str]]:
    """First pass: collect function names mapped to their parameter types.

    Handles single-line and multi-line function declarations.
    """
    func_types: dict[str, list[str]] = {}

    single_decls = []
    single_decls.extend(
        (m[0], m[1])
        for m in re.findall(
            r"function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*\w+)?", code
        )
    )
    for m in re.findall(
        r"const\s+(\w+)\s*=\s*(?:async\s*)?\s*(?:\(([^)]*)\)|([A-Za-z_$]\w*))\s*=>",
        code,
    ):
        single_decls.append((m[0], m[1] if m[1] is not None else m[2]))

    for func_name, params_str in single_decls:
        if not func_name:
            continue
        types = []
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue
            if ":" in param:
                type_part = param.split(":")[-1].strip()
                base_type = type_part.split("[")[0].split("<")[0].strip()
                types.append(base_type)
            else:
                types.append("")
        func_types[func_name] = types

    multi_line = re.findall(
        r"function\s+(\w+)\s*\(([\s\S]*?)\)\s*:\s*\w+",
        code,
    )
    for func_name, params_block in multi_line:
        if func_name in func_types:
            continue
        types = []
        clean = re.sub(r"//[^\n]*", "", params_block)
        clean = re.sub(r"/\*[\s\S]*?\*/", "", clean)
        for param in clean.split(","):
            param = param.strip()
            if not param:
                continue
            if ":" in param:
                type_part = param.split(":")[-1].strip()
                base_type = type_part.split("[")[0].split("<")[0].strip()
                types.append(base_type)
            else:
                types.append("")
        if types:
            func_types[func_name] = types

    return func_types


def _check_type_errors_typescript(code: str, feedback: dict) -> None:
    """Detect common TypeScript type errors.

    First pass: collect function declarations with typed parameters.
    Second pass: check function calls against declared types.
    Raises CodeTypeError if a type mismatch is found.
    """
    func_param_types = _collect_function_types(code)
    if not func_param_types:
        return

    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue

        for func_name, param_types in func_param_types.items():
            pattern = re.compile(r"\b" + re.escape(func_name) + r"\s*\(")
            for match in pattern.finditer(stripped):
                call_args = _extract_call_args(stripped, match.end() - 1)
                for arg_idx, arg_val in enumerate(call_args):
                    if arg_idx >= len(param_types):
                        break
                    param_type = param_types[arg_idx]
                    if not param_type:
                        continue
                    arg_type = _infer_arg_type(arg_val)

                    if _types_mismatch(param_type, arg_type):
                        raise CodeTypeError(
                            f"Type error: expected '{param_type}' but got '{arg_type}' in call to '{func_name}' (argument {arg_idx + 1})",
                            line=i,
                            column=stripped.index(arg_val) + 1 if arg_val in stripped else 1,
                            expected_type=param_type,
                            actual_type=arg_type,
                        )


def _types_mismatch(param_type: str, arg_type: str) -> bool:
    """Check if an argument type doesn't match the parameter type."""
    if not param_type or arg_type == "variable":
        return False
    if param_type == arg_type:
        return False
    if param_type in ("number", "string", "boolean") and arg_type in ("number", "string", "boolean"):
        return True
    if param_type == "any" or arg_type == "any":
        return False
    return False


def _extract_call_args(line: str, paren_pos: int) -> list[str]:
    """Extract arguments from a function call starting at the opening paren."""
    depth = 0
    current = ""
    args = []
    started = False
    for ch in line[paren_pos:]:
        if ch == "(":
            depth += 1
            started = True
            continue
        if not started:
            continue
        if ch == ")":
            depth -= 1
            if depth <= 0:
                if current.strip():
                    args.append(current.strip())
                break
        if ch == "," and depth == 1:
            args.append(current.strip())
            current = ""
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        current += ch
    return args


def _infer_arg_type(arg: str) -> str:
    """Infer the type of an argument value."""
    arg = arg.strip()
    if not arg:
        return "variable"
    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        return "string"
    if arg.startswith("`"):
        return "string"
    if re.match(r"^-?\d+(\.\d+)?$", arg):
        return "number"
    if arg in ("true", "false"):
        return "boolean"
    if arg == "null" or arg == "undefined":
        return "null"
    if arg.startswith("["):
        return "array"
    if arg.startswith("{"):
        return "object"
    return "variable"


def _analyze_python(code: str) -> tuple[dict[str, int], dict]:
    feedback: dict = {"issues": [], "suggestions": [], "highlights": []}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise CodeSyntaxError(
            f"Syntax error: {e.msg}",
            line=e.lineno,
            column=e.offset,
        ) from None

    complexity = _calc_complexity_python(tree, feedback)
    naming = _check_naming_python(tree, feedback)
    error_handling = _check_error_handling_python(tree, code, feedback)
    duplication = _check_duplication(code, feedback)
    security = _check_security_python(code, feedback)
    maintainability = _calc_maintainability(code, complexity)

    scores = {
        "complexity": complexity,
        "naming": naming,
        "error_handling": error_handling,
        "duplication": duplication,
        "security": security,
        "maintainability": maintainability,
    }
    return scores, feedback


def _analyze_typescript_javascript(code: str) -> tuple[dict[str, int], dict]:
    feedback: dict = {"issues": [], "suggestions": [], "highlights": []}

    brace_count = code.count("{") - code.count("}")
    paren_count = code.count("(") - code.count(")")
    if brace_count != 0:
        line = _find_line_for_brace_mismatch(code, "{", "}")
        raise CodeSyntaxError(
            f"Unbalanced braces: {abs(brace_count)} unmatched {'{' if brace_count > 0 else '}'}",
            line=line,
            column=1,
        )
    if paren_count != 0:
        line = _find_line_for_brace_mismatch(code, "(", ")")
        raise CodeSyntaxError(
            f"Unbalanced parentheses: {abs(paren_count)} unmatched '('",
            line=line,
            column=1,
        )

    _check_type_errors_typescript(code, feedback)

    lines = code.split("\n")
    func_count = len(re.findall(r"(function\s+\w+|const\s+\w+\s*=\s*\(|=>\s*\{|\w+\s*\(.*\)\s*\{)", code))
    avg_len = sum(len(l) for l in lines) / max(len(lines), 1)

    complexity = _clamp(10 - func_count // 2 - code.count("if ") // 3)
    naming = _clamp(8 if re.search(r"[a-z][a-zA-Z\d]*\s*[=:(]", code) else 5)
    error_handling = _check_error_handling_generic(code, feedback)
    duplication = _check_duplication(code, feedback)
    security = _clamp(10 if "eval(" not in code and "innerHTML" not in code else 3)
    maintainability = _clamp(10 if avg_len < 80 else 6)

    return {
        "complexity": complexity,
        "naming": naming,
        "error_handling": error_handling,
        "duplication": duplication,
        "security": security,
        "maintainability": maintainability,
    }, feedback


def _analyze_go(code: str) -> tuple[dict[str, int], dict]:
    feedback: dict = {"issues": [], "suggestions": [], "highlights": []}

    brace_count = code.count("{") - code.count("}")
    if brace_count != 0:
        line = _find_line_for_brace_mismatch(code, "{", "}")
        raise CodeSyntaxError(
            f"Unbalanced braces: {abs(brace_count)} unmatched {'{' if brace_count > 0 else '}'}",
            line=line,
            column=1,
        )

    has_err_check = "if err != nil" in code
    func_count = len(re.findall(r"func\s+\w+", code))
    has_goroutine = "go " in code

    complexity = _clamp(10 - func_count // 2)
    naming = _clamp(8 if re.search(r"func [A-Z]", code) else 6)
    error_handling = _check_error_handling_generic(code, feedback)
    duplication = _check_duplication(code, feedback)
    security = _clamp(8)
    maintainability = _clamp(9 if has_err_check else 6)

    if has_goroutine:
        feedback["highlights"].append("Uses goroutines for concurrency")
    if not has_err_check and func_count > 2:
        feedback["suggestions"].append("Add error handling (if err != nil) for functions that can fail")

    return {
        "complexity": complexity,
        "naming": naming,
        "error_handling": error_handling,
        "duplication": duplication,
        "security": security,
        "maintainability": maintainability,
    }, feedback


def _analyze_java(code: str) -> tuple[dict[str, int], dict]:
    feedback: dict = {"issues": [], "suggestions": [], "highlights": []}

    brace_count = code.count("{") - code.count("}")
    if brace_count != 0:
        line = _find_line_for_brace_mismatch(code, "{", "}")
        raise CodeSyntaxError(
            f"Unbalanced braces: {abs(brace_count)} unmatched {'{' if brace_count > 0 else '}'}",
            line=line,
            column=1,
        )

    has_try = "try" in code and "catch" in code
    class_count = len(re.findall(r"class\s+\w+", code))
    has_generics = "<" in code and ">" in code

    complexity = _clamp(10 - class_count)
    naming = _clamp(8 if re.search(r"class [A-Z][a-zA-Z]+", code) else 5)
    error_handling = _check_error_handling_generic(code, feedback)
    duplication = _check_duplication(code, feedback)
    security = _clamp(8)
    maintainability = _clamp(9 if has_generics else 7)

    return {
        "complexity": complexity,
        "naming": naming,
        "error_handling": error_handling,
        "duplication": duplication,
        "security": security,
        "maintainability": maintainability,
    }, feedback


def _analyze_cpp(code: str) -> tuple[dict[str, int], dict]:
    feedback: dict = {"issues": [], "suggestions": [], "highlights": []}

    brace_count = code.count("{") - code.count("}")
    if brace_count != 0:
        line = _find_line_for_brace_mismatch(code, "{", "}")
        raise CodeSyntaxError(
            f"Unbalanced braces: {abs(brace_count)} unmatched {'{' if brace_count > 0 else '}'}",
            line=line,
            column=1,
        )

    has_smart_ptr = "unique_ptr" in code or "shared_ptr" in code
    has_try = "try" in code and "catch" in code
    has_nullptr = "nullptr" in code

    complexity = _clamp(10 - code.count("for ") // 2 - code.count("while ") // 2)
    naming = _clamp(7)
    error_handling = _check_error_handling_generic(code, feedback)
    duplication = _check_duplication(code, feedback)
    security = _clamp(10 if has_smart_ptr else 6)
    maintainability = _clamp(10 if has_nullptr else 6)

    if has_smart_ptr:
        feedback["highlights"].append("Uses smart pointers for memory safety")
    if not has_nullptr:
        feedback["suggestions"].append("Consider using nullptr instead of NULL/null")

    return {
        "complexity": complexity,
        "naming": naming,
        "error_handling": error_handling,
        "duplication": duplication,
        "security": security,
        "maintainability": maintainability,
    }, feedback


def _calc_complexity_python(tree: ast.AST, feedback: dict) -> int:
    branches = sum(
        1 for node in ast.walk(tree)
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With))
    )
    score = _clamp(10 - branches // 2)
    if branches >= 5:
        feedback["issues"].append(f"High cyclomatic complexity: {branches} branch points")
    return score


def _check_naming_python(tree: ast.AST, feedback: dict) -> int:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            names.append(node.name)
        elif isinstance(node, ast.Name):
            names.append(node.id)

    if not names:
        return 8

    good = sum(1 for n in names if re.match(r"^[a-z_][a-z0-9_]*$", n) or re.match(r"^[A-Z]", n))
    score = _clamp(int(good / len(names) * 10))
    if score < 6:
        feedback["suggestions"].append("Use snake_case for functions/variables, PascalCase for classes")
    return score


def _check_error_handling_python(tree: ast.AST, code: str, feedback: dict) -> int:
    try_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
    func_count = max(sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)), 1)

    error_prone_patterns = ["open(", "requests.", "urllib", "socket", "connect(", "execute("]
    has_error_prone = any(p in code for p in error_prone_patterns)

    if has_error_prone and try_count == 0:
        feedback["issues"].append("Error-prone operations (file/network) without try/except")
        return 3

    if not has_error_prone and try_count == 0:
        return 8

    ratio = try_count / func_count
    score = _clamp(int(ratio * 15))
    if score < 5 and has_error_prone:
        feedback["suggestions"].append("Add try/except blocks around error-prone operations")
    return max(score, 6)


def _check_error_handling_generic(code: str, feedback: dict) -> int:
    has_try = any(kw in code for kw in ["try", "catch", "except", "except("])
    has_go_err = "if err != nil" in code
    has_error_handling = has_try or has_go_err

    error_prone = any(p in code for p in ["open(", "requests.", "connect(", "execute(", "fetch(", "os.", "ReadFile", "WriteFile"])

    if error_prone and not has_error_handling:
        feedback["issues"].append("Error-prone operations without error handling")
        return 3

    if not error_prone and not has_error_handling:
        return 8

    if has_go_err:
        return 9

    return 7


def _check_security_python(code: str, feedback: dict) -> int:
    issues = 0
    dangerous = {
        "eval(": "eval() executes arbitrary code",
        "exec(": "exec() executes arbitrary code",
        "pickle.loads": "pickle.loads can execute malicious payloads",
        "subprocess.call": "subprocess with shell=True is dangerous",
        "os.system": "os.system is vulnerable to injection",
    }
    for pattern, msg in dangerous.items():
        if pattern in code:
            issues += 1
            feedback["issues"].append(f"Security: {msg}")

    if issues == 0:
        feedback["highlights"].append("No obvious security vulnerabilities detected")
        return 10

    return _clamp(10 - issues * 5)


def _check_duplication(code: str, feedback: dict) -> int:
    lines = [l.strip() for l in code.split("\n") if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//")]
    if not lines:
        return 10
    counter = Counter(lines)
    dup_ratio = sum(c - 1 for c in counter.values() if c > 1) / max(len(lines), 1)
    score = _clamp(int(10 - dup_ratio * 30))
    if score < 7:
        feedback["suggestions"].append("Reduce code duplication — extract repeated logic into functions")
    return score


def _calc_maintainability(code: str, complexity_score: int) -> int:
    lines = code.split("\n")
    avg_len = sum(len(l) for l in lines) / max(len(lines), 1)
    long_lines = sum(1 for l in lines if l.rstrip() and len(l.rstrip()) > 100)
    score = _clamp((complexity_score + 10) // 2 - long_lines)
    return max(score, 1)


def _clamp(value: int, lo: int = 1, hi: int = 10) -> int:
    return max(lo, min(hi, int(value)))
