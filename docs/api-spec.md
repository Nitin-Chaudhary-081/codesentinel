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

All errors follow the RFC 7807 format:
```json
{
  "detail": "Description of the error"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Resource not found |
| 409 | Conflict (duplicate email) |
| 422 | Validation error |
| 500 | Internal server error |
