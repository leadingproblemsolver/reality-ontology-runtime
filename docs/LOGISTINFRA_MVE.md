# Logistinfra MVE

## Purpose

The MVE exists to stop execution from disappearing into chat/session memory.

It does **one thing**:

> hold one current transition, force one next move, require an observable settlement, and preserve enough durable state for a fresh process to continue without reconstructing the whole project.

No agent mesh. No global scheduler. No broad automation layer. No new ontology.

The existing Reality Ontology Runtime already provides the durable store, NextMove selector, timer, settlement contract, and minimal web surface. The Logistinfra MVE is the operational contract for using those pieces on live work.

---

## MVE contract

Every live workload is reduced to:

```text
TARGET
NOW
DELTA
CANDIDATES
→ exactly one selected NEXT MOVE
→ execute
→ external or inspectable RECEIPT
→ SETTLE
→ next mission
```

There may be only **one ACTIVE mission**.

A mission is not complete because work was attempted. It is complete only when it is settled as one of:

- `RECEIPT`
- `CAPABILITY_GAIN`
- `FALSIFIED_HYPOTHESIS`
- `EXPLICIT_KILL`
- `BLOCKED`

If the timebox expires, the next action is **settlement**, not invisible continuation.

---

## What is durable

The SQLite runtime stores:

- mission target;
- observed state;
- delta;
- candidate transitions;
- selected next move;
- append-only mission events;
- settlement observation;
- receipt locator;
- next action;
- bridged RealityStore evidence/settlement where available.

Model/session memory is not authoritative.

---

## First proving workload: GateOfAI

Current commercial state:

- 30-account GCC finance/procurement batch exists.
- 4 accounts already received generic/routing outreach and have no reply: GWC, RSA Global, Milaha, Bahri.
- 26 accounts are not yet contacted.
- live operator/workflow verification is incomplete.
- 0 accounts are qualified.
- 0 GateOfAI handoffs are ready.

Therefore the dependency-correct MVE transition is **not** “make another list” and **not** “spray messages”.

It is:

> Verify the highest-information 10 accounts and compile an evidence-backed top-5 SEND_QUEUE.

The checked-in mission spec is:

`examples/logistinfra_mve_gateofai.json`

---

## Run it

Requirements: Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

# initialize durable runtime
ro --db .runtime/logistinfra.db init

# start exactly one live transition
ro --db .runtime/logistinfra.db next-start \
  --spec examples/logistinfra_mve_gateofai.json

# show the current next move at any time
ro --db .runtime/logistinfra.db next

# optional minimal operator UI
ro --db .runtime/logistinfra.db serve --port 8787
# open http://127.0.0.1:8787/next
```

Execute the selected transition using the current worker/tool.

Do not open another execution loop until this mission is settled.

---

## Settlement examples

### Evidence-backed queue produced

```bash
ro --db .runtime/logistinfra.db next-settle RECEIPT \
  --observation "Top 10 processed; 6 verified, 4 rejected; evidence-backed top-5 SEND_QUEUE produced." \
  --receipt "/absolute/or/repo/path/to/updated_gateofai_batch.csv" \
  --next-action "Send the approved top 5 through authorized channels."
```

### Hypothesis falsified

```bash
ro --db .runtime/logistinfra.db next-settle FALSIFIED_HYPOTHESIS \
  --observation "The assumed AP owner roles were stale across the top accounts; current routing must be rebuilt." \
  --receipt "/path/to/verification_receipt.md" \
  --next-action "Replace stale operators before outreach."
```

### Blocked

```bash
ro --db .runtime/logistinfra.db next-settle BLOCKED \
  --observation "LinkedIn request state cannot be inspected from the available authorized session." \
  --next-action "Use the authorized LinkedIn session to verify request state."
```

### Kill

```bash
ro --db .runtime/logistinfra.db next-settle EXPLICIT_KILL \
  --observation "This transition does not change external reality or reduce a live dependency."
```

---

## Fresh-process recovery test

After settlement:

```bash
# close shell / restart process / start a fresh session
ro --db .runtime/logistinfra.db next
ro --db .runtime/logistinfra.db next-events <mission_id>
```

Acceptance condition:

A fresh process can answer, without reading prior chats:

1. What are we trying to change?
2. What was true when the mission started?
3. What gap remained?
4. What action was selected?
5. What actually happened?
6. What receipt proves it?
7. What is the next transition?

If those seven answers require reconstructing old chats, the MVE has failed.

---

## Deliberate exclusions

Not in the MVE:

- autonomous multi-pipeline scheduling;
- cross-chat automatic ingestion;
- LLM memory replacement;
- market opportunity discovery;
- CRM;
- arbitrary worker orchestration;
- vector search;
- full LCE integration;
- automated external mutations;
- dashboards beyond the existing `/next` view;
- scoring systems beyond the current strict NextMove rank.

Those are later only if the live MVE proves a repeated need.

---

## Definition of done

Logistinfra MVE is actual when one live GateOfAI transition completes this cycle:

```text
real current state
→ persisted mission
→ one selected action
→ action executed
→ inspectable receipt
→ explicit settlement
→ fresh-process recovery
→ next transition
```

That is the entire MVE.
