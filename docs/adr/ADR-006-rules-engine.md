# ADR-006 · Dynamic Business Rules Engine

**Date:** 2026-06-01  **Status:** Accepted

## Context

A real Sainapsis/Bridge requirement: business logic over order attributes
(country, amount, customer attributes) needs to change without deploys.
The previous test's `paymentFailed > $1000 → create_support_ticket` rule is
the canonical example — currently hardcoded in `PaymentFailedHandler`.

## Decision

A separate, additive rules engine layered on top of the state machine. Three
strictly separated concerns:

1. **Storage** — CRUD over `Rule` entities (in-memory in MVP, DynamoDB in v2)
2. **Evaluation** — pure recursive function over an AND/OR/NOT/Comparison tree
3. **Action execution** — registry of `ActionHandler`s (Strategy pattern, same
   shape as the existing `EventHandlerRegistry`)

Rules are triggered by:
- `order_created` — fires after a new order is persisted
- `event:<eventType>` — fires after each state transition

## Consequences (and what we accept)

- **Pydantic in the domain for rules.** `Rule` and `ConditionNode` are Pydantic
  models, not plain dataclasses like `Order`. Justified: rules are pure data
  (no behavior on the entity); the discriminated-union pattern for the AND/OR
  tree is dramatically cleaner with Pydantic; and the on-wire and in-memory
  shape stay identical, eliminating a mapping layer.
- **Synchronous evaluation, synchronous actions.** Acceptable for the MVP.
  Required for actions that mutate the order (taxes, fees) — they must take
  effect before persistence. For external-call actions (tickets, emails)
  async-via-SQS is the natural v2 evolution.
- **Hardcoded `PaymentFailedHandler` kept.** The engine is additive in this
  release. A production migration would remove the hardcoded handler in a
  follow-up PR after observing the rule fire in production logs.
- **Order entity carries `attributes: dict` and `adjustments: list`.** The
  former lets new rule-addressable fields (origin_country, etc.) be added
  without schema migrations. The latter keeps `order.amount` immutable and
  fully auditable — `total_amount` is a computed property.

## Rejected / Deferred

- **DSL-based conditions (JSONLogic / CEL).** More expressive but loses
  type-safe validation against a schema. Reconsider as an *escape hatch* in v2.
- **RETE-style indexing.** Premature for our expected rule counts. Re-evaluate
  if `RuleEvaluations` CloudWatch metric exceeds X per minute.
- **DynamoDB persistence for rules.** Deferred to keep the MVP focused. The
  `RuleRepository` ABC means swapping it in is a single new class.
- **Schema registry for valid fields/operators.** A `SCHEMA: dict[str, type]`
  constant + validator on rule creation is the obvious v2 — for the MVP we
  accept that a typo in `field` will just silently fail to match (covered by
  the dry-run endpoint).
