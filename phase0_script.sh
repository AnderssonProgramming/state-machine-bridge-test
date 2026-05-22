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