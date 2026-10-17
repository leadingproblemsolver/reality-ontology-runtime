# Moment Router

## Purpose

Eliminate the recurring cognitive/logistical cost of deciding **what to work on, which chat/operator to open, what context to load, and what the next move is**.

The Moment Router sits above all other Logistinfra operators. Its job is to reconstruct the present operating state and return only:

1. **one primary action**;
2. **one interruption lane** for genuinely urgent external events;
3. **the exact chat/operator to use**;
4. **the minimum context bundle to load**;
5. **the receipt that ends the block**.

It should not ask the user to choose among many chats unless the underlying evidence is genuinely tied.

---

## Core contract

```text
current moment
+ time/daypart
+ calendar/commitments
+ deadlines
+ waiting states
+ inbound replies/events
+ active goals
+ current blockers
+ current proof gaps
+ external opportunity freshness
+ energy/location/device constraints
+ unfinished executions
+ dependency graph
+ priority policy
        ↓
MOMENT ROUTER
        ↓
PRIMARY NOW
INTERRUPTION LANE
EXACT OPERATOR/CHAT
CONTEXT PACK
FIRST ACTION
STOP CONDITION
RECEIPT
NEXT RE-EVALUATION TRIGGER
```

The output must be executable without further navigation.

---

## Inputs

### A. Temporal
- current timestamp + timezone;
- day of week;
- daypart;
- time available before next hard commitment;
- deadline distance;
- follow-up due times;
- waiting windows that have expired.

### B. Reality state
- active goals;
- active projects;
- current project states;
- blockers;
- unresolved questions;
- explicit commitments;
- external receipts;
- failed/unknown executions;
- dependencies;
- latest evidence.

### C. External events
- new email/reply;
- GitHub issue/PR/review change;
- job/opportunity freshness;
- market signal freshness;
- calendar event proximity;
- customer/user response;
- system/deployment failure.

### D. Proof / consequence state
- highest-value missing evidence;
- proof level of each active artifact;
- whether a live external loop exists;
- whether a target is waiting on us;
- whether we are waiting on a target;
- whether a task would create state change, information gain, capability, or access.

### E. Execution constraints
- device: phone / desktop;
- location/context: local/Qatar vs global block when relevant;
- available duration;
- energy/cognitive load when explicitly supplied;
- tool/integration availability;
- authority/approval required.

---

## Priority law

Hard gates are evaluated before scoring.

### Hard preemption gates
1. Safety/security incident.
2. External actor waiting on us with a near-term consequence.
3. Deadline/meeting/application/commitment inside its action window.
4. Broken production/deployment blocking a live user or commitment.
5. Previously approved consequential action that is ready and time-sensitive.

If no hard gate fires, rank candidates using a simple inspectable score:

```text
priority =
  external_consequence
+ information_gain
+ deadline_pressure
+ dependency_unlock
+ relationship/access_value
+ proof_gain
+ probability_now
+ compounding_value
- switching_cost
- execution_cost
- reversibility_risk
- speculation_penalty
```

Do not let model judgment silently override hard rules.

---

## Candidate actions

Candidates should come from durable state, not brainstorming. Examples:
- send a due follow-up;
- respond to an inbound reply;
- reproduce a selected GitHub issue;
- finish a live deployment blocker;
- submit an application before deadline;
- run a scheduled market scan;
- verify a previously executed action;
- capture/convert a new proof receipt;
- perform the next dependency-correct human-owned gate;
- continue a paused block whose blocker has cleared.

Every candidate must name:
- goal it advances;
- current state;
- target state;
- required operator/chat;
- required context;
- expected receipt;
- estimated block length;
- why now.

---

## Output contract

The router must return at most this:

```yaml
moment:
  timestamp: ...
  available_minutes: ...
  next_hard_commitment: ...

primary:
  goal: ...
  project: ...
  action: ...
  why_now: ...
  operator: ...
  chat_reference: ...
  context_refs: [...]
  first_physical_action: ...
  stop_condition: ...
  receipt_required: ...
  timebox_minutes: ...

interruption_lane:
  condition: ...
  operator: ...
  action: ...

waiting:
  - item: ...
    next_check_at: ...

suppressed:
  - candidate: ...
    reason: ...

re_evaluate_when:
  - primary completed/failed
  - inbound external event
  - deadline enters action window
  - blocker clears
  - calendar boundary reached
```

No dashboard wall. No ten-option list.

---

## Chat/operator registry

Existing chats become operator definitions, each with explicit I/O rather than destinations the user must remember.

Example:

```yaml
operator_id: market_router
chat_title: Market Router
accepts:
  - live_target
  - signal
  - constraint
  - channel
  - artifact_inventory
returns:
  - next_external_action
  - artifact_to_use
  - claim_boundary
  - expected_receipt
invoke_when:
  - qualified external target exists
  - next intervention is not yet selected
```

The structuralization prompt pack should be used to progressively convert every relevant chat into this registry shape:

```text
INPUT
→ rules/transformation
→ tools
→ OUTPUT
→ acceptance
→ failure paths
→ next handoff
```

---

## Context compilation

The router must never dump full chat histories into the active operator.

For the selected action, compile only:
- exact objective;
- current verified state;
- decisive recent evidence;
- prior attempts/results;
- constraints;
- people/actors involved;
- relevant artifact/repo/URL;
- unresolved unknown;
- requested transition;
- claim/authority boundary.

The context bundle should be persisted and addressable by ID so the same action can be resumed from a fresh process.

---

## Interaction surface

The ideal user experience is one persistent entry point:

```text
NOW

Primary: Reproduce Browser Use #5438
Why: live contribution opportunity; highest current proof gap; 58 min free before next commitment
Open: GitHub Opportunity / Technical Proof operator
First action: run failing reproduction fixture
Done when: failing test + preserved trace

Interrupt only if: maintainer reply / urgent email / deadline event
```

Buttons/actions later:
- START
- DONE
- BLOCKED
- WRONG PRIORITY
- SNOOZE
- REJECT

The user's corrections become evidence for tuning policy; they must not silently mutate canonical rules without review.

---

## Automation cadence

Do not poll everything aggressively.

Recommended triggers:
- on session/open: always recompute;
- calendar boundary: recompute;
- inbound webhook/email/GitHub event: recompute;
- primary block completion/failure: recompute;
- hourly background scan only for sources where freshness matters;
- morning/daypart transition: compile the first action in advance.

---

## First implementation slice

Do not integrate every data source yet.

Implement Moment Router v0 against:
1. manually persisted active goals/tasks;
2. GitHub opportunity pipeline state;
3. calendar events;
4. executions/approvals/evidence tables;
5. operator registry for the first 5-10 existing chats;
6. deterministic ranking + optional LLM tie-break/explanation.

Acceptance test:

> From a fresh process, with at least three competing active items, the router reconstructs the current state and returns exactly one dependency-correct primary action, the correct operator/context pack, a stop condition and receipt, while suppressing inferior candidates with inspectable reasons.

Negative tests:
- urgent inbound external reply preempts ordinary planned work;
- waiting-on-external item is not repeatedly selected;
- expired/stale evidence lowers candidate confidence;
- insufficient time prevents selection of a task larger than the available window;
- completed item is not resurfaced;
- failed execution routes to diagnosis/recovery rather than repeating blindly;
- missing evidence is exposed rather than invented.

---

## End state

The user should no longer need to remember:
- which chat owns what;
- what was last decided;
- what is waiting;
- which project is more urgent;
- what context to paste;
- which tool/site to open first;
- when to follow up;
- whether to build, research, contact, verify, or settle.

The system should continuously answer:

> **Given what is true right now, what is the single highest-value dependency-correct action I can execute, which operator owns it, and what receipt ends it?**
