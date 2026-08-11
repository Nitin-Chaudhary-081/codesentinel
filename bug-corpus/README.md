# Bug Corpus — Intentional Bugs for Evaluation Testing

This directory contains intentional bugs across all supported languages.
Each bug is documented with its fix for testing the evaluation engine.

## Structure

```
bug-corpus/
├── python/
│   ├── bug-01-security-eval.md
│   ├── bug-02-missing-error-handling.md
│   └── ...
├── typescript/
├── go/
├── java/
├── javascript/
└── cpp/
```

## Categories

| Category | Description |
|----------|-------------|
| Security | Injection, unsafe eval, hardcoded secrets |
| Error Handling | Missing try/catch, swallowed exceptions |
| Naming | Unclear variable/function names |
| Duplication | Repeated code blocks |
| Complexity | Deeply nested logic, long functions |
| Maintainability | Magic numbers, no types, dead code |

## Usage

These examples are used to:
1. Verify the evaluation engine detects real issues
2. Test that fixed code scores higher
3. Demonstrate the platform's capabilities
