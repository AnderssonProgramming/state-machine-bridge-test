# ─── 5. .pre-commit-config.yaml ───────────────────────────────────────────────
log "Writing .pre-commit-config.yaml..."
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  # Enforces conventional commit format on every commit message
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.2.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, refactor, test, docs, ci, chore, perf]
EOF
ok ".pre-commit-config.yaml"

# ─── 6. CONTRIBUTING.md ───────────────────────────────────────────────────────
log "Writing CONTRIBUTING.md..."
cat > CONTRIBUTING.md << 'EOF'
# Contributing Guide

## Branch Model

```
main              ← production-ready, protected (merge from develop only)
  └── develop     ← integration branch, protected (merge from feature/* only)
        ├── feature/<short-description>
        ├── fix/<short-description>
        ├── refactor/<short-description>
        ├── test/<short-description>
        ├── docs/<short-description>
        └── ci/<short-description>
```

> ⚠️ Direct pushes to `main` and `develop` are **blocked** by branch rulesets.
> Every change must come through a Pull Request with all CI checks passing.

---

## Conventional Commits

Format: `<type>(<optional scope>): <description>`

| Type       | When to use                              |
|------------|------------------------------------------|
| `feat`     | New feature or endpoint                  |
| `fix`      | Bug fix                                  |
| `refactor` | Code change with no feature or fix       |
| `test`     | Adding or updating tests                 |
| `docs`     | Documentation only                       |
| `ci`       | CI/CD pipeline changes                   |
| `chore`    | Tooling, dependencies, configuration     |
| `perf`     | Performance improvement                  |

### Examples

```
feat(order): add state machine transition table
fix(handler): return 422 on invalid transition instead of 500
test(order-service): add paymentFailed handler unit tests
refactor(state-machine): extract transition lookup into named constant
ci(github-actions): add SonarCloud quality gate step
chore(deps): bump fastapi from 0.110.0 to 0.111.0
docs(adr): add ADR-001 backend runtime decision
```

---

## Pull Request Process

1. Branch off `develop`
2. Make atomic commits using conventional format
3. Open PR targeting `develop` (never directly to `main`)
4. All CI checks must pass: lint → type-check → tests → SonarCloud
5. Merge strategy: **Squash and merge**

---

## Local Setup

```bash
# Install pre-commit hooks (run once after cloning)
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

# Verify hooks work
pre-commit run --all-files
```
EOF
ok "CONTRIBUTING.md"

# ─── 7. PR Template ───────────────────────────────────────────────────────────
log "Writing .github/PULL_REQUEST_TEMPLATE.md..."
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Summary
<!-- One sentence: what does this PR do and why? -->

## Type of Change
- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `refactor` — no functional change
- [ ] `test` — tests only
- [ ] `ci` — pipeline change
- [ ] `docs` — documentation
- [ ] `chore` — tooling / deps

## Checklist
- [ ] Follows conventions (PEP 8, 88-char line length, f-strings, pathlib, named constants)
- [ ] Google-style docstrings on all public methods
- [ ] No magic strings or numbers
- [ ] Unit tests added / updated for changed logic
- [ ] All checks pass locally (`pytest`, `black --check`, `ruff`, `mypy`)
- [ ] No secrets or credentials committed

## Closes
<!-- closes #XX -->
EOF
ok ".github/PULL_REQUEST_TEMPLATE.md"

# ─── 8. ADR Skeletons ─────────────────────────────────────────────────────────
log "Writing ADR skeletons..."

cat > docs/adr/ADR-001-backend-runtime.md << 'EOF'
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
EOF

cat > docs/adr/ADR-002-deployment.md << 'EOF'
# ADR-002 · Deployment Target

**Date:** 2026-05-22  **Status:** Accepted

## Decision
- Backend  → AWS Lambda + API Gateway (free tier, HTTPS via ACM)
- Frontend → Vercel (free tier, automatic TLS)
- Storage  → DynamoDB (free tier: 25 GB / 25 RCU/WCU)
- IaC      → AWS SAM (template.yaml)

## Rejected Alternatives
- Duck DNS + Certbot: unnecessary complexity; API Gateway handles TLS natively
- Railway: valid, but Lambda is required for the seniority bonus
EOF

cat > docs/adr/ADR-003-frontend-stack.md << 'EOF'
# ADR-003 · Frontend Stack

**Date:** 2026-05-22  **Status:** Accepted

## Decision
React + Vite + TypeScript + TailwindCSS

Deliverables:
- Bonus A: Create Order Form
- Bonus B: Order State Viewer + valid-transitions dropdown
- Bonus C: Live State Machine Diagram via `reactflow`
EOF

cat > docs/adr/ADR-004-chatbot.md << 'EOF'
# ADR-004 · AI Chatbot

**Date:** 2026-05-22  **Status:** Accepted

## Decision
Claude API (Anthropic /v1/messages) with a compiled context file
`context/sainapsis_context.txt` containing:
- Sainapsis company + Bridge product knowledge
- Order State Machine domain knowledge

Capabilities:
- Answer questions about Bridge and the order system
- Create orders and trigger transitions via natural language
- Show current order state in the chat response
EOF

cat > docs/adr/ADR-005-quality-gates.md << 'EOF'
# ADR-005 · Quality Gates

**Date:** 2026-05-22  **Status:** Accepted

## Decision
- Black + Ruff  → formatting and linting on every commit (pre-commit)
- mypy          → static type checking on every commit (pre-commit)
- SonarCloud    → code quality analysis on every PR
- CodeQL        → security analysis on push to develop/main
- pip-audit     → dependency vulnerability scan on every PR
- pytest + cov  → ≥ 85% coverage target, report uploaded as PR artifact
EOF

ok "ADR skeletons (docs/adr/)"

# ─── 9. Backend Skeleton ──────────────────────────────────────────────────────
log "Writing backend skeleton..."

# __init__.py files
for dir in \
  backend/src \
  backend/src/domain \
  backend/src/services \
  backend/src/handlers \
  backend/src/repositories \
  backend/src/models \
  backend/tests \
  backend/tests/unit \
  backend/tests/integration; do
  touch "$dir/__init__.py"
done

cat > backend/src/main.py << 'EOF'
"""
 ██████╗ ██████╗ ██████╗ ███████╗██████╗
██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║   ██║██████╔╝██║  ██║█████╗  ██████╔╝
██║   ██║██╔══██╗██║  ██║██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝

Order Processing State Machine — Sainapsis Technical Test
Author: Andersson David Sánchez Méndez
        Escuela Colombiana de Ingeniería Julio Garavito
"""

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(
    title="Order Processing State Machine",
    description="Sainapsis Backend Technical Test — Andersson Sánchez",
    version="1.0.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


# AWS Lambda ASGI handler
handler = Mangum(app)
EOF

cat > backend/requirements.txt << 'EOF'
fastapi==0.111.0
mangum==0.17.0
pydantic==2.7.1
uvicorn[standard]==0.29.0
aws-lambda-powertools[all]==2.38.0
boto3==1.34.0
anthropic==0.26.0
EOF

cat > backend/requirements-dev.txt << 'EOF'
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-cov==5.0.0
httpx==0.27.0
black==24.4.2
ruff==0.4.4
mypy==1.10.0
pre-commit==3.7.1
pip-audit==2.7.3
EOF

ok "backend/src/main.py + requirements*.txt"

# ─── 10. Environment template ─────────────────────────────────────────────────
log "Writing .env.example..."
cat > .env.example << 'EOF'
# ── Persistence ───────────────────────────────────────────────────────────────
REPOSITORY_BACKEND=memory        # memory | dynamodb
DYNAMODB_TABLE_NAME=orders
AWS_REGION=us-east-1

# ── AI Chatbot ────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY=your-key-here

# ── Runtime ───────────────────────────────────────────────────────────────────
ENVIRONMENT=local                # local | staging | production
LOG_LEVEL=INFO
POWERTOOLS_SERVICE_NAME=order-state-machine
EOF
ok ".env.example"

# ─── 11. context/ placeholder ─────────────────────────────────────────────────
cat > context/sainapsis_context.txt << 'EOF'
# Sainapsis Context File
# Phase 3 — Populate this file with compiled Sainapsis + Bridge knowledge.
# Used as the system-prompt context for the AI chatbot feature.
#
# Sections to fill:
#   1. Sainapsis — company overview, mission, certifications, tech partners
#   2. Bridge    — product description, features, industries, tech stack
#   3. Order SM  — states, transitions, business rules (for domain Q&A)
EOF
ok "context/sainapsis_context.txt (placeholder)"

# ─── 12. GitHub Actions placeholder ───────────────────────────────────────────
cat > .github/workflows/.gitkeep << 'EOF'
# CI/CD workflows are defined in Phase 6.
# Files to be created:
#   ci.yml        — lint + type-check + tests + SonarCloud  (on PR)
#   security.yml  — CodeQL + pip-audit                      (on push to develop/main)
#   deploy.yml    — SAM build + Lambda deploy + Vercel      (on merge to main)
EOF
ok ".github/workflows/ (placeholder for Phase 6)"

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Phase 0 scaffold complete ✓                     ${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo ""
echo "  Next steps (manual):"
echo ""
echo "  1. Commit the scaffold:"
echo "       git add ."
echo "       git commit -m 'chore: phase 0 repo scaffold'"
echo "       git push origin main"
echo ""
echo "  2. Create and push develop branch:"
echo "       git checkout -b develop"
echo "       git push -u origin develop"
echo ""
echo "  3. Install pre-commit hooks:"
echo "       pip install pre-commit"
echo "       pre-commit install"
echo "       pre-commit install --hook-type commit-msg"
echo ""
echo "  4. Configure GitHub Branch Rulesets (see instructions below)."
echo ""
warn "Don't forget to configure GitHub Rulesets before starting Phase 1!"
echo ""