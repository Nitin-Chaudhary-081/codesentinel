# Architecture Decision Records

## ADR 001 — Database: Supabase PostgreSQL vs Self-Hosted

**Status:** Accepted

**Context:** Need a production-grade PostgreSQL database without infrastructure management.

**Decision:** Use Supabase free tier (500MB) as the primary PostgreSQL provider.

**Consequences:**
- (+) Zero setup, managed backups, connection pooling
- (+) Free tier sufficient for development and small-scale production
- (-) Vendor lock-in; can migrate to self-hosted PG via connection string change
- (-) Cold start on free tier after inactivity

---

## ADR 002 — Evaluation Engine Architecture

**Status:** Accepted

**Context:** Need to evaluate code quality across 6 languages with consistent scoring.

**Decision:** Modular analyzer pattern — each language has a dedicated analyzer function returning a standardized `ScoreBreakdown` dict.

**Consequences:**
- (+) Easy to add new languages
- (+) Consistent scoring rubric across languages
- (-) Some analyzers are simpler than others (Python has AST, others use regex)
- (-) Not a full compiler-level analysis

---

## ADR 003 — Caching Strategy: Content-Hash + Redis

**Status:** Accepted

**Context:** Code evaluation is expensive; same code submitted twice should return cached results.

**Decision:** SHA-256 content hash as cache key. Primary cache: Upstash Redis (free tier). Fallback: local file-based `{hash}.json`.

**Consequences:**
- (+) Path-independent caching (same code = same hash)
- (+) Auto-invalidating on content change
- (+) Graceful degradation if Redis unavailable
- (-) Redis free tier has command limits (10K/day)
