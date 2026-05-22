# ADR-001 · Backend Runtime

**Date:** 2026-05-22  **Status:** Accepted

## Context
The seniority bonus requires AWS Lambda + Powertools. Local development must
remain ergonomic (fast feedback, no cloud dependency).

## Decision
FastAPI + Mangum adapter, deployed to AWS Lambda.

- FastAPI → clean 3-layer architecture, Pydantic v2 validation
- Mangum → ASGI-to-Lambda adapter: `handler = Mangum(app)` (one line)
- AWS Powertools → Logger, Tracer, Metrics via Lambda layers
- Local: `uvicorn backend.src.main:app --reload`
- Production: Lambda invokes `handler`

## Consequences
Same codebase runs locally and on Lambda with zero divergence.