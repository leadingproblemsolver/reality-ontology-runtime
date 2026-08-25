# Reality Ontology Runtime

**An evidence-bounded control layer for agentic execution.**

Reality Ontology Runtime exists to answer one operational question:

> **What actually happened, what is true now, and what is the next action we are allowed to take?**

It does **not** try to replace coding agents, browser agents, MCP servers, or workflow engines. Those systems execute work. This runtime governs the parts they usually leave ambiguous: durable reality, authority, verification, settlement, contradictions, and recovery after a process or model session disappears.

Canonical ontology: [`ontology/CANONICAL_REALITY_ONTOLOGY.yaml`](ontology/CANONICAL_REALITY_ONTOLOGY.yaml)  
Status: **V1 locked**  
Runtime: Python + SQLite  
Execution substrate currently integrated: **Goose headless + MCP**

---

## Why this exists

Agent runtimes are good at producing actions. They are much weaker at proving the resulting state.

The dangerous case is simple:

```text
agent calls tool
→ external side effect succeeds
→ worker/model/process dies before recording success
→ system sees no local success
→ retry fires
→ duplicate external effect
```

Reality Ontology Runtime refuses to infer reality from the executor's return path.

Instead:

```text
GOAL
→ RECONSTRUCT CURRENT REALITY
→ CONSTRAIN
→ PROPOSE
→ AUTHORIZE
→ EXECUTE
→ OBSERVE / REREAD EXTERNAL STATE
→ VERIFY
→ RECORD EVIDENCE
→ DERIVE NEW STATE
→ SETTLE
→ REPLAN
```

A tool saying "success" is not proof.  
A timeout saying "failure" is not proof.  
**Fresh observation of the target system is proof.**

---

## The ownership boundary

The system is intentionally split into three layers.

### 1. Reality Ontology owns truth and settlement

It owns:

- canonical actors, goals, objects, relations;
- immutable evidence and events;
- derived current state;
- assumptions, contradictions, and decision validity;
- risk and approval boundaries;
- attempt lifecycle;
- independent verification;
- settlement receipts;
- fresh-process reconstruction.

### 2. Execution substrates own doing

Goose, MCP servers, shell tools, browser/computer operators, and future external adapters may:

- inspect files and repositories;
- execute shell/code changes;
- invoke APIs;
- call MCP tools;
- mutate external systems.

They do **not** get to declare canonical reality.

### 3. Planners/LLMs own interpretation and proposals

A planner may:

- decompose a goal;
- identify likely constraints;
- request context;
- propose candidate next actions.

It may **not**:

- establish exact reality;
- bypass approval;
- mark an external effect verified without reread;
- mutate canonical state directly.

---

## Canonical primitives

### Reality primitives

```text
Actor
Goal
Object
State
Event
Evidence
Relation
```

### Validity primitives

```text
Assumption
RealitySignal
Contradiction
Decision
DecisionOutcome
```

### Execution primitives

```text
Transition
ExecutionContract
Operator
Permission
Attempt
Verification
SettlementReceipt
Handoff
```

---

## Hard invariants

V1 locks these semantics:

1. **State is derived, not declared.**
2. **Claim strength never exceeds evidence strength.**
3. **Truth states are not flattened.**
4. **Execution and verification are separate.**
5. **External uncertainty requires reread before retry.**
6. **No consequential run ends unsettled.**
7. **Settlement requires context to be updated.**
8. **Assumptions are append-only and statused.**
9. **Contradictions connect assumptions to reality signals.**
10. **Invalidated assumptions reopen dependent decisions.**
11. **LLMs interpret reality; deterministic evidence establishes exact reality.**
12. **Model/session state is not Reality Store state.**
13. **Embeddings are retrieval aids, not source truth.**
14. **Consequential mutation requires explicit authority.**
15. **Fresh-process recovery is required.**
16. **Duplicate evidence is not independent support.**
17. **Canonical relations require provenance.**
18. **Renaming does not create new canonical objects.**
19. **External evidence outranks internal narrative.**

Runtime code and integrations may extend V1, but may not silently weaken these rules.

---

## Truth ladder

Artifacts and workflows move only as far as evidence supports:

```text
DISCUSSED
→ DECIDED
→ PREPARED
→ IMPLEMENTED
→ TESTED
→ DEPLOYED
→ EXPOSED
→ EXTERNALLY_USED
→ REUSED
→ ADOPTED
→ PAID
→ OUTCOME_PRODUCING
```

For example, an internal deployment script cannot promote something to `EXTERNALLY_USED`; that requires external-use evidence.

---

## Permission model

```text
L0_READ
  automatic

L1_REVERSIBLE_WRITE
  automatic within policy

L2_EXTERNAL_CONSEQUENTIAL
  human approval by default
```

The current Goose operator is deliberately `L2_EXTERNAL_CONSEQUENTIAL` because a general execution runtime can create real external effects.

---

## Attempt lifecycle

```text
PLANNED
→ RUNNING
→ WAITING_EXTERNAL / SUSPENDED / FAILED_*
→ SUCCEEDED_UNVERIFIED
→ VERIFIED
→ SETTLED
```

`SUCCEEDED_UNVERIFIED` is a critical state.

It means:

> the executor returned, but Reality Ontology has not yet independently proven the requested state transition.

Likewise, a timeout is not automatically a failure. If an external side effect may have occurred, the runtime reconciles the target system before considering a retry.

---

## How execution works

A `TransitionContract` declares:

- the object being changed;
- the goal it serves;
- required entry state;
- desired resulting state;
- operator;
- operation;
- risk level.

The execution engine then performs:

```text
1. resolve operator
2. confirm operator risk matches contract
3. enforce approval for L2
4. reconstruct current object state
5. enforce entry-state precondition
6. persist attempt
7. prepare operator
8. execute
9. store SUCCEEDED_UNVERIFIED
10. independently verify via fresh reread
11. persist evidence
12. if verification fails: FAILED_RETRYABLE
13. if verified: record event
14. derive new state
15. write settlement receipt
16. mark attempt SETTLED
17. reconstruct from durable store on next process
```

The core implementation is in [`src/reality_ontology/executor.py`](src/reality_ontology/executor.py).

---

## Real execution: Goose + MCP

The first real execution substrate is [`GooseHeadlessOperator`](src/reality_ontology/operators/goose_headless.py).

It supports:

### Task mode

```text
Reality
→ Goose headless
→ built-in developer tools
→ filesystem/shell/code work
→ deterministic reread
→ verification
→ settlement
```

### Recipe/MCP mode

```text
Reality
→ Goose recipe
→ MCP server
→ external API
→ external mutation
→ fresh external reread
→ verification
→ evidence
→ settlement
```

Goose's stdout, stderr, return code, timeout state, and invocation metadata are retained as execution information, but none of those alone establish truth.

---

## Proven external failure case

The repository contains a live GitHub Actions hostile smoke test.

Workflow:

[`goose-mcp-external-smoke`](.github/workflows/goose-mcp-smoke.yml)

Verified run:

**GitHub Actions run `32861760131`**

The workflow installed the actual Goose CLI `1.47.0`, started a real MCP stdio server, and used the workflow-scoped GitHub token to create reversible GitHub issues.

### Normal path

```text
Goose
→ MCP create issue
→ external GitHub issue exists
→ Reality rereads GitHub
→ verifies exact marker
→ records evidence
→ settles
→ fresh process reconstructs EXPOSED
```

Receipt:

- issue `#7`
- `goose_timed_out=false`
- evidence `ev_4475c9712e544686`
- settlement `settlement_0d9e9a9fe5164216`
- fresh-process state `EXPOSED`

### Ambiguous side-effect path

The MCP server deliberately:

```text
creates GitHub issue
→ persists transport receipt
→ stalls for 30 seconds
```

Reality's Goose caller times out after 8 seconds.

So from the caller's perspective:

```text
tool result = missing
external side effect = uncertain
```

The runtime does **not** replay the mutation.

Instead:

```text
timeout
→ fresh GitHub reread
→ reconcile exact run marker
→ prove one matching issue
→ record evidence
→ settle
→ reopen store in fresh process
→ reconstruct EXPOSED
```

Receipt:

- issue `#8`
- `goose_timed_out=true`
- evidence `ev_8c463cb358a44de5`
- settlement `settlement_ab70970e09614b12`
- fresh-process state `EXPOSED`

Both probe issues were closed after verification.

This proves the V1 critical invariant:

```text
external effect may have occurred
→ caller misses success
→ reread external truth
→ do not duplicate mutation
→ evidence
→ settlement
→ fresh-process recovery
```

The workflow also retains the Reality SQLite databases, MCP transport receipts, and provider log as an Actions artifact.

---

## Quick start

Requirements:

- Python 3.11+
- SQLite
- Goose only if running Goose-backed execution

Install:

```bash
git clone https://github.com/leadingproblemsolver/reality-ontology-runtime.git
cd reality-ontology-runtime

python -m venv .venv
source .venv/bin/activate

python -m pip install -e '.[dev]'
pytest
```

Run the local deterministic demo:

```bash
ro --db .runtime/reality.db demo
ro --db .runtime/reality.db reality
```

The demo:

1. initializes the Reality Store;
2. creates the bounded workflow state;
3. performs a reversible local transition;
4. independently rereads the target;
5. records verification evidence;
6. writes an event;
7. derives the new state;
8. creates a settlement receipt;
9. closes/reopens durable state;
10. reconstructs the result.

---

## CLI

```bash
ro init
ro demo
ro reality
ro timeline <object_id>
ro context <goal_id>
ro verify-invariants
```

---

## Repository map

```text
.
├── ontology/
│   ├── CANONICAL_REALITY_ONTOLOGY.yaml   # V1 locked synthesis
│   ├── 01_GOVERNING_INVARIANTS.yaml
│   ├── 02_CANONICAL_ONTOLOGY.yaml
│   ├── 03_TRUTH_EVIDENCE_ASSUMPTION_MODEL.yaml
│   ├── 04_TRANSITION_EXECUTION_SETTLEMENT.yaml
│   ├── 05_CONTEXT_CONTINUITY.yaml
│   ├── 07_FAILURE_MODES_AND_HOSTILE_TESTS.yaml
│   ├── 09_JSON_SCHEMAS/
│   ├── MANIFEST.json
│   └── SHA256SUMS.txt
│
├── src/reality_ontology/
│   ├── models.py
│   ├── store.py
│   ├── executor.py
│   ├── truth.py
│   ├── verification.py
│   └── operators/
│       ├── file_marker.py
│       └── goose_headless.py
│
├── scripts/
│   ├── github_smoke_mcp.py
│   ├── run_goose_mcp_smoke.py
│   ├── verify_github_issue.py
│   └── close_github_smoke_issue.py
│
├── examples/
├── tests/
├── docs/
└── .github/workflows/
```

---

## Reality Store

SQLite currently stores the durable canonical ledger for:

- actors;
- goals;
- objects;
- evidence;
- events;
- relations;
- approvals;
- attempts;
- settlements;
- assumptions;
- decisions;
- decision dependencies;
- reality signals;
- contradictions.

Derived state is reconstructed from that history rather than trusted as an unsupported assertion.

---

## Context continuity

Context is not an unbounded chat transcript.

A context packet is a bounded projection of durable Reality containing the pieces needed for the next transition.

The intended recovery property is:

```text
kill model session
kill worker
start fresh process
open Reality Store
reconstruct current truth
recover unresolved state
select next legal transition
continue
```

This is why model memory, embeddings, and conversation history are explicitly below the Reality Store in authority.

---

## What this does not claim

V1 does **not** claim:

- exactly-once delivery for arbitrary external systems;
- production-scale distributed locking;
- arbitrary host-crash recovery at every instruction boundary;
- production-scale performance;
- first-class Gmail/browser/CRM operators;
- superior LLM planning quality;
- replacement of mature agent/workflow runtimes.

Those require their own external evidence.

---

## Extension contract

New domains should usually be projections over this kernel:

```text
domain
→ goals
→ canonical objects
→ states
→ evidence rules
→ operators
→ constraints
→ transitions
→ verification
→ settlement
```

Examples already mapped conceptually include:

- SignalOps;
- Logistinfra;
- Reality Handoff;
- ContextOS / LCE;
- REF Execution OS.

The rule is:

> **Reuse mature execution systems. Add ontology/runtime infrastructure only when a real failure forces a missing primitive.**

---

## V1 acceptance contract

Reality Ontology V1 is considered satisfied when a fresh process can:

```text
reconstruct a real workflow from durable evidence
→ identify the legal transition
→ enforce authority
→ execute through a bounded operator
→ independently verify the external result
→ persist evidence
→ derive state
→ settle context
→ restart
→ recover the verified state without model/session memory
```

That contract is now implemented for the local demo and proven against one live external GitHub mutation path, including the ambiguous timeout-after-side-effect case.

---

## Canonical source

Start here:

[`ontology/CANONICAL_REALITY_ONTOLOGY.yaml`](ontology/CANONICAL_REALITY_ONTOLOGY.yaml)

Then inspect:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/WORKING_STATE.md`](docs/WORKING_STATE.md)
- [`ontology/01_GOVERNING_INVARIANTS.yaml`](ontology/01_GOVERNING_INVARIANTS.yaml)
- [`ontology/04_TRANSITION_EXECUTION_SETTLEMENT.yaml`](ontology/04_TRANSITION_EXECUTION_SETTLEMENT.yaml)
- [`ontology/07_FAILURE_MODES_AND_HOSTILE_TESTS.yaml`](ontology/07_FAILURE_MODES_AND_HOSTILE_TESTS.yaml)

The ontology is now **V1 locked**. Change it only when new external evidence or hostile execution demonstrates that one of its semantics is wrong or incomplete.
