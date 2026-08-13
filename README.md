# CodeSentinel

![CI](https://github.com/YOUR_USERNAME/codesentinel/actions/workflows/ci.yml/badge.svg)

> Production-grade AI-powered code review and evaluation platform.
> Full Stack: Next.js 15 (TypeScript) + Flask 3.1 (Python) + PostgreSQL

---

## What It Does

CodeSentinel evaluates code quality, maintainability, and standards adherence across
TypeScript, Python, Go, Java, JavaScript, and C++. Developers submit code snippets and
receive structured, per-dimension scores (complexity, naming, error handling, duplication,
security, maintainability) plus actionable feedback — with every evaluation exportable as
JSONL, making the results directly reusable as high-quality AI training data.

---

## Tech Stack

- **Frontend:** Next.js 15.5.23, TypeScript, Tailwind CSS
- **Backend:** Flask 3.1, Python 3.14, SQLAlchemy (sync), JWT auth
- **Database:** SQLite (default, PostgreSQL-ready — set DATABASE_URL in .env)
- **Testing:** PyTest (92% coverage), Jest (81% coverage), Playwright E2E
- **CI:** GitHub Actions

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally

### Backend

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in JWT_SECRET and DATABASE_URL
flask run --port 8000
```

### Frontend

```bash
cd web
npm ci
cp .env.example .env.local   # fill in NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

---

## API Documentation

API contract: [`docs/api-spec.md`](docs/api-spec.md)

All endpoints require JWT Bearer token except `POST /auth/register`,
`POST /auth/login`, and `GET /health`.

Key endpoints:

- `POST /submissions` — submit code for evaluation
- `GET /submissions/{id}` — retrieve submission
- `POST /evaluations/{id}` — trigger evaluation
- `GET /reports/{id}/export` — export as JSON or JSONL (AI training format)

---

## Security

- **Dependencies:** 0 vulnerabilities (`npm audit` clean — Next.js 15.5.23 +
  postcss 8.5.26 + sharp 0.35.3 overrides applied)
- **Auth:** JWT HS256, expiry enforced, algorithm pinned
- **Input:** all submissions validated, static analysis only (no code execution)
- **Secrets:** zero real secrets in codebase or git history
- Audit report: [`docs/security/audit-after.json`](docs/security/audit-after.json)

Note: `pip-audit` blocked on aarch64/Android build environment (Rust compiler
constraint). Python deps pinned to exact versions in `requirements.txt`.

---

## Test Coverage

| Layer | Tool | Coverage | Status |
|---|---|---|---|
| Backend | PyTest | 92% | ✅ 62 passed |
| Frontend | Jest | 81% | ✅ 12 passed |
| E2E | Playwright | 5 flows | ✅ 5/5 passed |

Run tests:

```bash
# Backend
cd api && pytest --cov=. --cov-report=term

# Frontend
cd web && npm test

# E2E (backend must be running)
cd web && npm run test:e2e
```

---

## Architecture Decisions

Key decisions documented in [`docs/adrs.md`](docs/adrs.md):

- ADR 001: Database: Supabase PostgreSQL vs Self-Hosted
- ADR 002: Evaluation Engine Architecture
- ADR 003: Caching Strategy: Content-Hash + Redis

---

## Demo

- Recorded demo video: `web/test-results/**/video.webm` (login → submit → evaluate → report)
- Screenshots: `web/e2e/artifacts/*.png` (landing, dashboard, history, report)

---

## Environment Variables

See `.env.example` for required variables:

**Backend (`api/.env.example`):**
- `DATABASE_URL` — SQLAlchemy connection string (SQLite by default, PostgreSQL ready)
- `REDIS_URL` — optional Redis (Upstash or local)
- `JWT_SECRET` — strong, non-default value (required to start)
- `JWT_ALGORITHM` — `HS256`
- `JWT_EXPIRATION_HOURS` — token lifetime
- `DEBUG` — `true`/`false`
- `LOG_LEVEL` — `INFO`

**Frontend (`web/.env.example`):**
- `NEXT_PUBLIC_API_URL` — backend base URL (`http://localhost:8000`)
- `NEXT_PUBLIC_APP_NAME` — app display name

---

## License

MIT
