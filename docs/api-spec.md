# CodeSentinel API Specification

## OpenAPI 3.1

### Endpoints

#### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Create new account |
| POST | `/api/v1/auth/login` | Get JWT token |

#### Submissions

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/submissions` | Submit code for review |
| GET | `/api/v1/submissions` | List user submissions |
| GET | `/api/v1/submissions/{id}` | Get submission details |

#### Evaluations

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/evaluations/{submission_id}` | Run evaluation |
| GET | `/api/v1/evaluations/{submission_id}` | Get evaluation results |

#### Reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/reports/{submission_id}/export?format=markdown\|jsonl` | Export report |

### Schemas

#### ScoreBreakdown
```json
{
  "complexity": { "type": "integer", "minimum": 1, "maximum": 10 },
  "naming": { "type": "integer", "minimum": 1, "maximum": 10 },
  "error_handling": { "type": "integer", "minimum": 1, "maximum": 10 },
  "duplication": { "type": "integer", "minimum": 1, "maximum": 10 },
  "security": { "type": "integer", "minimum": 1, "maximum": 10 },
  "maintainability": { "type": "integer", "minimum": 1, "maximum": 10 }
}
```

#### Submission
```json
{
  "id": { "type": "integer" },
  "user_id": { "type": "integer" },
  "code": { "type": "string", "maxLength": 100000 },
  "language": { "enum": ["typescript", "python", "go", "java", "javascript", "cpp"] },
  "context": { "type": "string", "nullable": true },
  "status": { "enum": ["pending", "processing", "completed", "failed"] },
  "created_at": { "type": "string", "format": "date-time" },
  "updated_at": { "type": "string", "format": "date-time" }
}
```

### Error Responses

All errors use a consistent envelope (not RFC 7807):
```json
{
  "status": "error",
  "error_type": "validation_error",
  "message": "Code is required",
  "details": {}
}
```

| Status | `error_type` | Meaning |
|--------|--------------|---------|
| 400 | `validation_error` | Missing/invalid field (e.g. empty code, bad email, short password) |
| 400 | `unsupported_language` | Language not in the supported set |
| 401 | `unauthorized` | Missing or invalid bearer token |
| 404 | `not_found` | Submission or evaluation not found |
| 409 | `conflict` | Email already registered |
| 422 | `syntax_error` / `type_error` | Static analysis failure |
| 429 | `rate_limited` | Too many auth attempts |
| 500 | `server_error` / `analysis_failed` | Unexpected server/analysis error |

> Note: This is a Flask application, so there is no auto-served `/docs`
> OpenAPI endpoint. This document is the authoritative contract. A future
> FastAPI migration could auto-generate `/openapi.json` and `/docs`.
