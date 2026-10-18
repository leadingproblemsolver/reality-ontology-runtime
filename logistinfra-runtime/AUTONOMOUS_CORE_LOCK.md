# Logistinfra Autonomous Core Lock

## Decision

Stop treating context, routing, execution, marketing, OSS contribution, corporate outreach, proof, and follow-up as separate systems.

They are workstreams inside ONE runtime.

The core runtime is permanently:

```text
EVENT / USER INTENT
        ↓
SYNC
        ↓
REALITY ONTOLOGY
        ↓
ACTIVE WORKSTREAMS + WAITING + BLOCKERS
        ↓
MOMENT ROUTER
        ↓
MARKET ROUTER if market-facing
        ↓
CONTEXT PACK
        ↓
EXECUTOR
        ↓
TOOL / MODEL / CLAUDE CODE / BROWSER / HUMAN
        ↓
FRESH OBSERVATION
        ↓
VERIFY
        ↓
RECEIPT
        ↓
SETTLE
        ↓
ROUTE NEXT
        ↺
```

Everything else is an adapter or workstream.

## Core objects

Only these are canonical:

- SOURCE_EVENT
- CLAIM / EVIDENCE
- CHAT_REGISTRY
- WORKSTREAM_CAPSULE
- TRANSITION
- CONTEXT_PACKET
- EXECUTION
- APPROVAL
- RECEIPT
- WAKE_CONDITION
- ROUTE_DECISION
- FEEDBACK / EVAL_CASE

Do not add a new top-level architecture object without proving the current model cannot represent the requirement.

## Core services

### 1. SYNC
Ingest changed external state and update affected canonical objects.

### 2. ROUTE
Return one highest-value admissible transition.

### 3. EXECUTE
Invoke the selected bounded tool/model/operator.

### 4. VERIFY
Observe external state independently from the action call.

### 5. SETTLE
Commit only verified state change.

### 6. WAKE
Re-run routing only when an event, expiry, completion, failure, or deadline materially changes admissibility/priority.

## Autonomous execution law

Read-only/reversible operations may run automatically when policy permits.

Consequential external writes require explicit authority unless a durable scoped approval already exists.

Human-only transitions return a prepared packet rather than pretending they executed.

No execution settles itself.

`tool success != outcome success`.

## Agent role

Agents are workers, not authorities.

An agent receives:
- transition
- minimum context
- authority
- tools
- stop condition
- receipt contract

It returns:
- execution observation
- evidence
- uncertainty
- candidate receipt

Reality Ontology and deterministic policy decide what becomes canonical.

## Workstream examples

These are NOT separate architectures:

- Browser Use maintainer contribution
- Gmail → HubSpot paid pilot
- Microsoft/startup institutional credibility
- verified-transition OSS extraction
- internship applications
- Logistinfra productization
- technical foundation reps
- relationships/follow-ups

Each is just:
`CURRENT_STATE → NEXT_TRANSITION → RECEIPT`

## Anti-loop rule

If discussion proposes a new strategy/system, first ask:

1. Which existing workstream/object cannot represent it?
2. Which current transition is blocked?
3. What external receipt would the proposed system enable?
4. Can an existing connector/operator execute it?
5. Can the autonomous kernel route it already?

If answers do not expose a concrete missing runtime capability, do not create new architecture.

## First production acceptance gate

The core is operational only when it can autonomously run one mixed portfolio:

- one GitHub/OSS workstream;
- one market/client workstream;
- one waiting external workstream;
- one hard deadline/commitment;

and correctly:

1. SYNC live state;
2. choose one transition;
3. auto-execute a permitted read/reversible action;
4. stop for approval on a consequential write;
5. execute after approval;
6. independently verify;
7. SETTLE;
8. suppress waiting work;
9. wake on a real event;
10. route the next transition without manual reconstruction.

Until this passes, do not add product features, dashboards, additional agent frameworks, or new routing doctrines.
