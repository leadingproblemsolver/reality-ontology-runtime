# Reality Ontology Runtime

This repository is the executable V0 of the canonical Reality Ontology.

It enforces one closed loop:

```text
GOAL
→ RECONSTRUCT CURRENT STATE
→ SELECT NEXT VALID TRANSITION
→ PREPARE
→ AUTHORIZE
→ EXECUTE
→ REREAD / OBSERVE
→ VERIFY
→ RECORD EVIDENCE
→ DERIVE NEW STATE
→ SETTLE
→ REPLAN
```

## Hard invariants

1. **State is derived, never declared.** Canonical truth is an immutable event/evidence ledger.
2. **Claim strength never exceeds evidence strength.**
3. **Execution and verification are separate.** A tool returning success yields at most `SUCCEEDED_UNVERIFIED`.
4. **Uncertain external side effects are reconciled before retry.**
5. **No consequential run ends unsettled.**
6. **Model/session state is not Reality Store state.** A fresh process must recover state from SQLite.
7. **LLMs may interpret reality later; deterministic code establishes exact reality wherever possible.**
8. **Consequential writes require explicit authority.**

The full governing spec is versioned under [`ontology/`](ontology/). Runtime code must not silently weaken it.

## What actually runs today

- SQLite Reality Store with immutable evidence/events.
- Actors, goals, canonical objects, relations.
- Current-state reconstruction from event history.
- Truth-state promotion guard.
- Assumptions, decisions, reality signals, contradictions, dependency invalidation.
- Transition / execution contracts.
- Operator registry with explicit risk and approval levels.
- Execute → reread → verify pipeline.
- Persisted attempts with `SUCCEEDED_UNVERIFIED → VERIFIED → SETTLED` semantics.
- Settlement receipts.
- Context packet compilation from durable state.
- Fresh-process restart recovery.
- CLI and hostile tests.

## Fast start

```bash
python -m pip install -e '.[dev]'
pytest
ro --db .runtime/reality.db demo
ro --db .runtime/reality.db reality
```

The demo creates a real local workflow, executes one bounded filesystem transition, independently rereads the target, verifies the marker, records evidence, mutates derived state, settles the run, closes the database, reopens it in a fresh process object, and reconstructs the final state.

## CLI

```bash
ro init
ro demo
ro reality
ro timeline <object_id>
ro context <goal_id>
ro verify-invariants
```

## Runtime architecture

```text
                 Context Compiler
                       │
                       ▼
                  Planner boundary
                       │ proposes
                       ▼
                Permission Engine
                       │
                       ▼
                 Operator Registry
                       │
                 prepare / execute
                       │
                       ▼
               external/local system
                       │
                independent reread
                       │
                       ▼
                  Verification
                       │
                       ▼
         Evidence + Event + Settlement
                       │
                       ▼
                  Reality Store
                       │
                  state projection
```

## Extension rule

A new venture/domain should be configuration over this kernel—goals, objects, operators, constraints, progress model—not another architecture. Add new infrastructure only after a real workflow forces it.

## Acceptance test for V0

Starting with no model-session memory, the runtime must reconstruct a workflow, execute one bounded transition, independently verify it, settle it, then survive restart with the verified state and next transition recoverable.
