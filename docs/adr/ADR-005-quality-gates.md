# ADR-005 · Quality Gates

**Date:** 2026-05-22  **Status:** Accepted

## Decision
- Black + Ruff  → formatting and linting on every commit (pre-commit)
- mypy          → static type checking on every commit (pre-commit)
- SonarCloud    → code quality analysis on every PR
- CodeQL        → security analysis on push to develop/main
- pip-audit     → dependency vulnerability scan on every PR
- pytest + cov  → ≥ 85% coverage target, report uploaded as PR artifact
