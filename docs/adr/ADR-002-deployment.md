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
