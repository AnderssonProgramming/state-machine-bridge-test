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
