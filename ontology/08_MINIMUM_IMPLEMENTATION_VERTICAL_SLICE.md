# Minimum Dependency-Correct Vertical Slice

The smallest implementation that proves the Reality Ontology is not a conceptual framework is one closed loop.

## Acceptance target
Given a real goal and durable context, a fresh process can:

1. reconstruct current state;
2. identify an outstanding external transition;
3. prepare the exact action;
4. identify required authority;
5. obtain approval where necessary;
6. execute via a bounded operator;
7. independently verify the external result;
8. persist evidence;
9. derive the new state;
10. settle the run;
11. identify the next transition;
12. restart and reconstruct all of the above.

Anything less leaves a critical ontology claim unproven.

## Build order

### Phase 1 — Reality Store
Implement only:

- `Actor`
- `Goal`
- `Object`
- `Event`
- `Evidence`
- `Relation`
- `Execution/Attempt`

Use one canonical database.

Minimum API:

```text
record_event(...)
attach_evidence(...)
get_object_state(...)
get_goal_state(...)
get_timeline(...)
relate(...)
```

No agent rewrites memory. It records evidence/events. State is projected.

### Phase 2 — Current Reality projection
Command/API answers:

- current goals
- current object states
- constraints
- blockers
- open loops
- previous attempts
- waiting external states
- highest-confidence next transition

### Phase 3 — Context Compiler
Compile only what is required for the selected transition:

```text
objective
current_state
relevant_history
decisions
constraints
evidence
actors
open_loops
previous_attempts
authoritative_sources
uncertainties
requested_transition
```

### Phase 4 — Deterministic/LLM boundary
Deterministic code owns exact state and execution facts.

LLM may interpret, rank hypotheses, decompose ambiguity, and propose interventions.

The LLM does not establish durable truth when exact sources exist.

### Phase 5 — Operator contract
Every action has:

```text
prepare
execute
verify
rollback
```

plus:

```text
preconditions
expected_transition
risk
authority
maximum_scope
proof_required
```

### Phase 6 — Permission Engine
Start with:

- L0 READ — automatic
- L1 REVERSIBLE WRITE — automatic within policy
- L2 EXTERNAL / CONSEQUENTIAL — explicit approval

### Phase 7 — Durable attempts
Persist:

`PLANNED → RUNNING → ... → SUCCEEDED_UNVERIFIED → VERIFIED → SETTLED`

Never retry uncertain external side effects without reread.

### Phase 8 — Settlement
A run cannot terminate until state, evidence, context, open loops, next transition, and handoff are synchronized.

### Phase 9 — Reality Enforcer
Add:

- assumption extraction
- reality signals
- contradiction records
- dependency graph
- decision outcome measurement
- invalidation propagation
- exclusion of invalid decisions from active context

### Phase 10 — Generalize only from repeated real workflows
Do not build a huge abstract platform first.

A domain integration is configuration/policy over the same kernel:

```text
goals
objects
operators
constraints
progress_model
```

The common substrate should emerge from repeated execution, not precede it as speculative architecture.

## Hard proof condition
The vertical slice passes only when a fresh process can reconstruct a real workflow after restart and continue safely from the exact prior verified state.
