# Proof Surfaces + Preproof Embedding

Proof is not a post-processing step. P-1 should be built so every meaningful implementation emits an inspectable proof object by default.

## Ranked proof surfaces

### 1. External acceptance / external operational receipt
Strongest early surface.

Examples:
- merged upstream PR;
- maintainer-requested change accepted;
- real operator uses the output and confirms/corrects it;
- buyer routes, qualifies, or authorizes a next step.

Why first:
another person has spent scarce attention or changed external state because of the work.

### 2. Independent reproduction
A fresh person/process can reproduce the behavior from public artifacts without private chat state.

For Logistinfra:
- clone repo;
- run tests;
- start mission;
- compile block;
- settle;
- restart;
- recover correct next action.

### 3. Hostile / failure-mode proof
Demonstrate correct behavior under the failure the system claims to handle.

Examples:
- process dies after side effect;
- stale state arrives;
- interrupt arrives mid-block;
- assumption is contradicted;
- timebox expires without receipt.

### 4. Ecosystem-native contribution
Existing work packaged in the conventions of a community people already use.

Examples:
- n8n workflow/template;
- n8n community node;
- issue reproduction + accepted patch;
- reference integration.

### 5. Real repeated use
Same user/operator/workflow uses it again.

This upgrades "worked once" into continuity/adoption evidence.

### 6. Public benchmark / comparison
A small reproducible benchmark against a baseline.

Use only after the underlying behavior is stable.

### 7. Public proof note / case study
Short explanation linking:
problem → artifact → test → receipt → limitation → next test.

Useful distribution layer, weaker than the receipt it summarizes.

### 8. Social engagement
Views, likes, reposts, stars.

Useful for distribution, weak as validity evidence.

---

# Preproof embedding contract

Before implementing any P-1 component define:

```yaml
claim:
failure_case:
input_fixture:
expected_behavior:
hostile_test:
receipt:
independent_reproduction:
external_receiver:
claim_ceiling_before:
claim_ceiling_after:
next_external_test:
```

A feature without this contract should not enter the P-1 implementation queue unless it is required by a feature that has one.

---

# P-1 proof map

## `ro resume`

Claim:
fresh-process state recovery without reconstructing chats.

Preproof:
- persisted live mission;
- prior settlement;
- restart process;
- exact recovered next action.

Proof:
unit test + CLI transcript + fresh-process reproduction.

Externalization:
upstream reliability/workflow community example.

## `ro block`

Claim:
selected transition compiles deterministically into a bounded 10/25-minute executable envelope.

Preproof:
- same durable mission;
- exact expected receipt;
- deterministic phase plan;
- stop condition.

Proof:
tests + CLI JSON output.

Externalization:
reference implementation for human-in-the-loop agent execution.

## Attention firewall

Claim:
low-value novelty cannot silently replace active execution.

Preproof:
inject H1 email during active mission and H5 critical event separately.

Proof:
event timeline preserves current mission or records explicit safe interruption + restart cue.

## Decision invalidation

Claim:
strong contradiction can invalidate an assumption and stale dependent decisions.

Preproof:
known assumption/decision dependency + contradictory receipt.

Proof:
before/after decision state + event trace.

## Procedural memory

Claim:
repeated verified executions become reusable procedure candidates without overfitting from one run.

Preproof:
three comparable settled runs.

Proof:
1 run no promotion; 2 candidate; 3 promotable.

## GateOfAI live workload

Claim:
P-1 can move a real commercial workload without rebuilding state in chat.

Proof hierarchy:
verified account/operator evidence → sent-message receipt → real reply → workflow confirmation → qualification → GateOfAI handoff → quotation → close/commission.

---

# Rule

Every block emitted by `ro block` contains a `preproof` object.

That object is the bridge from implementation to proof externalization.
