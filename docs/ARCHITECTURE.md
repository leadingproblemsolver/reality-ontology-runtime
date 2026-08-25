# Architecture

Reality Ontology Runtime is a deliberately small event-sourced execution kernel.

```text
Goal / Current State
       ↓
Context Compiler
       ↓
Planner boundary (proposal only)
       ↓
Permission Engine
       ↓
Operator Contract
prepare → execute → reread → verify
       ↓
Evidence / Event / Settlement
       ↓
Reality Store (SQLite V0)
       ↓
Derived current-state projection
```

Canonical truth is the durable event/evidence ledger plus canonical object identity. Model output, session memory, dashboard status, and embeddings are non-canonical.

## Runtime boundaries

- Deterministic code establishes exact state wherever possible.
- LLMs may later interpret observations and propose transitions; they do not own canonical state.
- External/consequential writes require explicit authority.
- A tool success result produces at most `SUCCEEDED_UNVERIFIED`.
- State promotion occurs only after independent verification.
- Consequential runs terminate only after settlement updates durable state, evidence, context, open loops, and next transition.
