# CodeSentinel — AI Code Review & Evaluation Platform

Production-grade full stack platform for evaluating code quality, maintainability,
and standards adherence across TypeScript, Python, Go, Java, JavaScript, and C++.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Next.js 14 Frontend (port 3000)            │
├─────────────────────────────────────────────┤
│  FastAPI Backend (port 8000)                │
├─────────────────────────────────────────────┤
│  PostgreSQL (Supabase or local)             │
│  Redis (Upstash or in-memory)               │
└─────────────────────────────────────────────┘
```

## Quick Start

```bash
# Backend
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

# Frontend (separate terminal)
cd web
npm install
npm run dev
```

## Project Structure

```
codesentinel/
├── api/              # FastAPI backend
│   ├── src/          # Application source
│   └── tests/        # PyTest tests
├── web/              # Next.js frontend
│   ├── src/          # Application source
│   └── tests/        # Jest tests
├── shared/           # Shared types, schemas
├── bug-corpus/       # Intentional bug examples per language
├── docs/             # ADRs, specs
├── scripts/          # Dev scripts
└── .github/          # PR templates, CI
```

## License
MIT
