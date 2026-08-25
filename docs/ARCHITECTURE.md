# Architecture

## Canonical vs derived

**Canonical:** actor/object/goal identity, evidence, events, relations, attempts, approvals, settlements, assumptions/signals/contradictions.

**Derived:** current object state, goal progress, context packets, timelines, decision validity, next-transition candidates.

Never persist a derived projection as a replacement for its event/evidence basis.

## Deterministic / LLM boundary

The current runtime deliberately has no LLM dependency. Exact state, verification, authority, truth-state promotion, and settlement are deterministic.

A future planner may propose:
- likely constraints;
- retrieval needs;
- decompositions;
- candidate interventions.

It may not directly establish durable truth or bypass operators/policy.

## Durable execution semantics

`PLANNED → RUNNING → WAITING_EXTERNAL / FAILED_* / SUCCEEDED_UNVERIFIED → VERIFIED → SETTLED`

A missing local success record never proves an external action did not happen. Reconcile external state before retry.
