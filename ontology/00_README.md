# Reality Ontology — Canonical Source-of-Truth Pack
Version: 2026-08-25
Status: CANONICAL_SYNTHESIS
Scope: Reality Ontology → Reality Enforcer / LCE / ContextOS → Logistinfra → Reality Handoff / SignalOps / REF Execution OS

## Canonical definition
A local, event-sourced model of reality that preserves actors, goals, objects, states, events, evidence, relations, uncertainty, assumptions, decisions, provenance, authority, and outcomes so that:

1. current state can be reconstructed rather than asserted;
2. legal next transitions can be selected under constraints;
3. consequential actions are bounded by explicit authority;
4. action success is independently verified against the external system;
5. evidence and resulting state are durably written back;
6. contradictions invalidate or re-open dependent decisions;
7. a fresh human/agent/process can recover what is true without relying on chat/session memory.

## Core loop
REALITY
→ SIGNALS
→ CONTEXT
→ MODEL
→ DECISION
→ BOUNDED ACTION
→ OBSERVED OUTCOME
→ EVIDENCE
→ VERIFICATION
→ SETTLEMENT
→ UPDATED REALITY

Operational compression:

GOAL
→ RECONSTRUCT CURRENT STATE
→ IDENTIFY CONSTRAINT
→ SELECT NEXT VALID TRANSITION
→ PREPARE
→ AUTHORIZE
→ EXECUTE
→ REREAD / OBSERVE
→ VERIFY
→ RECORD EVIDENCE
→ MUTATE DERIVED STATE
→ SETTLE
→ SELECT NEXT TRANSITION

## What this is not
- Not a knowledge graph whose edges are accepted merely because an LLM inferred them.
- Not a dashboard state variable such as `project.status = doing`.
- Not model/session memory.
- Not a vector database.
- Not a planning ontology detached from external execution.
- Not a second parallel framework beside Logistinfra/REF.
- Not “AI says success” as a substitute for external verification.
- Not activity volume represented as progress.

## Pack layout
- `01_GOVERNING_INVARIANTS.yaml` — hard rules that may not be silently weakened.
- `02_CANONICAL_ONTOLOGY.yaml` — primitive objects, relations, statuses and reconstruction semantics.
- `03_TRUTH_EVIDENCE_ASSUMPTION_MODEL.yaml` — claim boundaries, assumptions, signals, contradictions.
- `04_TRANSITION_EXECUTION_SETTLEMENT.yaml` — state transition, operator, approval, verification and settlement contracts.
- `05_CONTEXT_CONTINUITY.yaml` — context packet and handoff rules.
- `06_LINEAGE_AND_PROJECTIONS.md` — how the ontology projects into LCE, Logistinfra, SignalOps, REF, market/proof systems.
- `07_FAILURE_MODES_AND_HOSTILE_TESTS.yaml` — adversarial tests and forbidden false-state patterns.
- `08_MINIMUM_IMPLEMENTATION_VERTICAL_SLICE.md` — smallest dependency-correct implementation.
- `09_JSON_SCHEMAS/` — machine-readable event/evidence/settlement schemas.
- `10_SOURCE_TRACE.md` — source lineage and exact source locations used.
- `CANONICAL_REALITY_ONTOLOGY.yaml` — merged machine-readable master spec.
- `MANIFEST.json` / `SHA256SUMS.txt` — integrity metadata.
