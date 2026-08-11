# Contributing to CodeSentinel

## Branching Strategy

- `main` — production-ready, protected
- `feature/<name>` — new features
- `fix/<name>` — bug fixes
- `docs/<name>` — documentation

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Go code analyzer
fix: handle syntax errors in Python evaluation
docs: update API specification
test: add edge case tests for TypeScript
refactor: extract scoring logic
```

## Development Setup

1. Clone the repo
2. Backend: `cd api && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. Frontend: `cd web && npm install`
4. Copy `.env.example` to `.env` in both directories
5. Run: `./scripts/start-backend.sh` and `./scripts/start-frontend.sh`

## Pull Request Process

1. Create a feature branch from `main`
2. Write tests FIRST (TDD)
3. Implement the feature
4. Ensure all tests pass: `./scripts/test-all.sh`
5. Open PR using the template
6. CI must pass before merge
