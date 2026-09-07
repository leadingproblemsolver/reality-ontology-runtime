# Reality Ontology Runtime

**A small runtime for one hard problem: knowing what actually happened after software, an agent, or a workflow tries to change the world.**

Execution tools are good at *doing things*. They are much less reliable at answering:

- Did the external change really happen?
- What evidence proves it?
- Is the result verified or only assumed?
- Is it safe to retry?
- What is true after the process, worker, or model session disappears?

Reality Ontology Runtime keeps those questions separate from the executor itself.

It records durable evidence, reconstructs current state, enforces approval boundaries, verifies external effects independently, and settles each consequential transition before the next action is chosen.

> A tool saying `success` is not proof. A timeout saying `failure` is not proof. Fresh observation of the target system is proof.

---

## If you came here from the construction-planning post

Start with these five surfaces, in this order:

1. **[Public proof summary](docs/CONSTRUCTION_PUBLIC_PROOF.md)** — plain-language problem, exact receipt, limits, and next real-world test.
2. **[Expected change-impact output](examples/construction/expected/change_impact.csv)** — the actual source-linked CSV produced by the checked-in fixture.
3. **[Construction tests](tests/test_construction_planning.py)** — deterministic regression, failure cases, provenance checks, and byte-identical rerun check.
4. **[Construction implementation](src/reality_ontology/domains/construction_planning/core.py)** — parsing, readiness projection, schedule diff, provenance, and impact construction.
5. **[Full construction contract](docs/CONSTRUCTION_PLANNING_MVP.md)** — input contract, statuses, assumptions, hard failures, and known limitations.

The public proof is tracked in **[PR #13](https://github.com/leadingproblemsolver/reality-ontology-runtime/pull/13)**.

### What that proof does

A planning engineer often has to combine several imperfect sources:

```text
current schedule
+ previous schedule
+ activity relationships
+ QA / document requirements
→ work out what changed
→ work out what is blocked
→ work out what preparation is now due
→ explain where each conclusion came from
```

The construction slice makes that comparison deterministic and inspectable.

Given:

- current activity export;
- previous activity export;
- predecessor/successor relationships;
- QA/document requirements;

it produces:

```text
90_day_readiness.csv
schedule_changes.csv
change_impact.csv
projection_receipt.json
```

One checked-in example is activity `A130`:

```text
planned start: 2026-12-20 → 2026-11-20
movement:      -30 days
lookahead:     entered the 90-day window
readiness:     BLOCKED
blocked by:    A120
requirement:   Final inspection dossier
evidence:      KNOWN
```

The row also retains references to the previous schedule row, current schedule row, current activity evidence, and requirement evidence.

That means the system does not just say *"A130 moved earlier."* It carries enough source information for a planner or engineer to inspect why the downstream status exists.

### Verified boundary

The construction proof is intentionally narrow.

It currently demonstrates:

- deterministic schedule comparison;
- source-linked readiness and change-impact output;
- explicit `KNOWN` vs `UNRESOLVED` evidence state;
- checked-in golden output;
- repeated output that must be byte-identical;
- automated tests and GitHub CI.

It **does not** claim:

- validation against a real Primavera P6 export schema;
- correctness on a live construction project;
- engineer acceptance;
- production use;
- measured time saving or accuracy improvement;
- adoption or commercial value.

The next useful evidence event is not another feature. It is running the existing pipeline against one anonymized real planning cycle and giving the output back to the engineer for correction.

---

## Run the construction proof

Requirements: Python 3.11+

```bash
git clone https://github.com/leadingproblemsolver/reality-ontology-runtime.git
cd reality-ontology-runtime
git checkout feat/construction-lookahead-mvp

python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

pytest

ro construction-lookahead \
  --activities examples/construction/activities.csv \
  --relationships examples/construction/relationships.csv \
  --requirements examples/construction/qa_requirements.csv \
  --previous-activities examples/construction/previous_activities.csv \
  --with-impact \
  --as-of 2026-09-04 \
  --days 90 \
  --output-dir artifacts/construction-demo
```

Expected output:

```text
artifacts/construction-demo/
├── 90_day_readiness.csv
├── schedule_changes.csv
├── change_impact.csv
└── projection_receipt.json
```

If you only want to inspect the expected result without running anything, open **[`examples/construction/expected/change_impact.csv`](examples/construction/expected/change_impact.csv)**.

---

# What the runtime itself does

The construction slice is one domain built on a more general runtime.

The underlying problem is common in agents and automation:

```text
agent calls tool
→ external side effect succeeds
→ process dies before recording success
→ local system sees no success
→ retry fires
→ duplicate external effect
```

A normal executor often knows what it *attempted*. It may not know what is now *true*.

Reality Ontology Runtime separates those concerns.

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

The important split is:

### Execution owns doing

A shell tool, MCP server, coding agent, browser operator, API client, or other executor can perform work.

### Verification owns proving

The runtime independently rereads the target system and checks whether the requested state actually exists.

### Durable state owns continuity

Evidence, events, attempts, settlements, assumptions, contradictions, and current derived state live outside model/session memory so a fresh process can reconstruct what happened.

---

## Concrete failure case already exercised

The repository also contains a live GitHub/MCP hostile test for an ambiguous external side effect.

The sequence is deliberately hostile:

```text
MCP creates a GitHub issue
→ side effect exists
→ MCP stalls
→ caller times out
→ caller cannot trust its own return path
```

The runtime does **not** immediately retry the mutation.

It instead:

```text
timeout
→ reread GitHub
→ find the exact external marker
→ verify one matching issue exists
→ record evidence
→ settle the transition
→ restart from durable state
→ recover the verified result
```

See:

- [`scripts/run_goose_mcp_smoke.py`](scripts/run_goose_mcp_smoke.py)
- [`scripts/github_smoke_mcp.py`](scripts/github_smoke_mcp.py)
- [`docs/GOOSE_INTEGRATION.md`](docs/GOOSE_INTEGRATION.md)

This is the core invariant the runtime is built around:

> **External uncertainty requires rereading external truth before retry.**

---

# Quick start: core runtime

Requirements:

- Python 3.11+
- SQLite
- Goose only for Goose-backed execution paths

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

1. initializes the durable store;
2. creates a bounded workflow object;
3. performs a reversible local transition;
4. independently rereads the target;
5. records verification evidence;
6. derives the new state;
7. writes a settlement receipt;
8. closes the process;
9. reopens the store;
10. reconstructs the settled state without model/session memory.

---

## Core CLI

```bash
ro init
ro demo
ro reality
ro timeline <object_id>
ro context <goal_id>
ro verify-invariants
```

Construction:

```bash
ro construction-lookahead --help
```

Next-move / mission control:

```bash
ro next-start --spec <mission.json>
ro next
ro next-events <mission_id>
ro next-settle <outcome> --observation "..."
```

---

# Mental model

You do not need the full ontology to understand the runtime.

The smallest useful model is:

```text
Something should change
→ decide who is allowed to change it
→ attempt the change
→ independently observe what is now true
→ attach evidence
→ derive state from that evidence
→ settle the transition
→ only then choose the next move
```

The durable objects behind that flow include:

```text
Goal
Object
Evidence
Event
Attempt
Verification
SettlementReceipt
Assumption
RealitySignal
Contradiction
Decision
```

The detailed ontology is in [`ontology/CANONICAL_REALITY_ONTOLOGY.yaml`](ontology/CANONICAL_REALITY_ONTOLOGY.yaml).

---

## Hard invariants

The runtime is designed around a few rules that should remain true across domains:

1. State is derived, not simply declared.
2. Claim strength cannot exceed evidence strength.
3. Execution and verification are separate.
4. A timeout is not automatically proof of failure.
5. External uncertainty requires reread before retry.
6. Consequential mutations require explicit authority.
7. Every consequential run should end settled.
8. Model/session memory is not the durable reality store.
9. Assumptions stay visible and can be invalidated by new evidence.
10. External evidence outranks internal narrative.

The full invariant set is in [`ontology/01_GOVERNING_INVARIANTS.yaml`](ontology/01_GOVERNING_INVARIANTS.yaml).

---

# Truth ladder

The repo uses explicit evidence levels so a project cannot silently promote itself from *built* to *used* or *valuable*.

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

For example:

- passing tests can support `TESTED`;
- a deployment can support `DEPLOYED`;
- a public URL can support `EXPOSED`;
- none of those prove `EXTERNALLY_USED`;
- only real external-use evidence can do that.

That boundary matters throughout this repository, including the construction proof.

---

# Repository guide

If you are reviewing the repo for a specific reason, use this path:

| Goal | Start here |
|---|---|
| Understand the construction proof quickly | [`docs/CONSTRUCTION_PUBLIC_PROOF.md`](docs/CONSTRUCTION_PUBLIC_PROOF.md) |
| Inspect actual construction output | [`examples/construction/expected/change_impact.csv`](examples/construction/expected/change_impact.csv) |
| Audit construction behavior/tests | [`tests/test_construction_planning.py`](tests/test_construction_planning.py) |
| Inspect construction implementation | [`src/reality_ontology/domains/construction_planning/core.py`](src/reality_ontology/domains/construction_planning/core.py) |
| Understand construction assumptions/limits | [`docs/CONSTRUCTION_PLANNING_MVP.md`](docs/CONSTRUCTION_PLANNING_MVP.md) + [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md) |
| Understand the runtime architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Inspect execution/settlement logic | [`src/reality_ontology/executor.py`](src/reality_ontology/executor.py) |
| Understand durable state | [`src/reality_ontology/store.py`](src/reality_ontology/store.py) |
| Inspect Goose/MCP execution | [`docs/GOOSE_INTEGRATION.md`](docs/GOOSE_INTEGRATION.md) |
| Understand next-move logic | [`docs/NEXTMOVE.md`](docs/NEXTMOVE.md) |
| Inspect the canonical ontology | [`ontology/CANONICAL_REALITY_ONTOLOGY.yaml`](ontology/CANONICAL_REALITY_ONTOLOGY.yaml) |
| See current working boundaries | [`docs/WORKING_STATE.md`](docs/WORKING_STATE.md) |

Top-level structure:

```text
.
├── docs/                  # human-readable contracts and proof surfaces
├── examples/              # inspectable fixtures and expected outputs
├── ontology/              # canonical semantics and invariants
├── scripts/               # hostile/live execution probes
├── src/reality_ontology/  # runtime + domain implementation
└── tests/                 # deterministic and failure-path tests
```

---

# Current boundaries

This repository does **not** claim:

- exactly-once delivery for arbitrary external systems;
- production-scale distributed locking;
- arbitrary crash recovery at every instruction boundary;
- production-scale performance;
- universal agent planning quality;
- support for every external system;
- that synthetic construction fixtures prove real P6 correctness;
- that tested software has automatically produced user or business outcomes.

Those claims require new external evidence.

---

# What should happen next

For the construction slice, the next transition is deliberately external:

```text
one anonymized real planning cycle
→ run existing pipeline unchanged
→ return source-linked output to engineer
→ collect corrections / acceptance / rejection
→ update only what real workflow evidence disproves
```

For the runtime more broadly, the rule is the same:

> **Do not add a new primitive because it sounds useful. Add it when a real execution path or external workflow demonstrates that the current model is insufficient.**

That keeps the repository evidence-bounded rather than architecture-led.
