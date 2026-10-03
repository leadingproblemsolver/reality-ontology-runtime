# Claude Code Prompt — Moment Router v0

Implement the first executable Moment Router inside the existing Logistinfra runtime.

Read first:
- `logistinfra-runtime/MOMENT_ROUTER.md`
- `logistinfra-runtime/README.md`
- `logistinfra-runtime/INTEGRATIONS.md`

## Goal

Eliminate manual chat/task switching by computing the single highest-value dependency-correct action for the present moment and returning the exact operator/chat + minimal context required to execute it.

Do not build a dashboard or a general productivity app.

## v0 Inputs

Use only:
1. persisted active goals/tasks;
2. existing `executions`, `approvals`, `evidence`, `signals`, `opportunities` state;
3. GitHub opportunity pipeline state;
4. calendar-shaped events through an adapter interface (fixture first if no live auth is present);
5. operator registry for 5-10 existing chat/operators;
6. current timestamp + declared available minutes.

## Implement

### 1. Operator registry
Create a typed registry where each operator has:
- `operator_id`
- `chat_title`
- `accepts`
- `returns`
- `invoke_when`
- `context_requirements`
- `stop_condition_template`

Seed at least:
- `results_shipping_artifact_map`
- `operational_research_strategy`
- `market_router`
- `message_triage`
- `next_steps_execution_plan`
- `evidence_to_impact`
- `github_opportunity`
- `production_project`
- `end_of_day_settlement`

### 2. Candidate compiler
Compile executable candidate actions only from persisted state.

Each candidate must contain:
- goal/project
- current state
- target state
- operator
- context refs
- external consequence
- information gain
- deadline pressure
- dependency unlock
- access/relationship value
- proof gain
- probability now
- switching cost
- execution cost
- risk
- speculation penalty
- required minutes
- receipt required
- why now

Do not let the model invent candidates unsupported by persisted state.

### 3. Hard preemption rules
Before scoring, deterministically preempt for:
1. safety/security incidents;
2. external actor waiting on us with near-term consequence;
3. deadline/meeting/application/commitment entering its action window;
4. production/deployment failure blocking a live commitment;
5. previously approved consequential action that is ready and time-sensitive.

### 4. Ranking
Implement deterministic inspectable scoring from `MOMENT_ROUTER.md`.

Allow an LLM only for:
- extracting structured fields from unstructured evidence when necessary;
- tie-breaking among near-equal candidates;
- producing the short `why_now` explanation.

The model may not override hard gates.

### 5. Context compiler
For the winning candidate, compile only:
- objective;
- current verified state;
- decisive recent evidence;
- previous attempts/results;
- constraints;
- actors;
- artifact/repo/URL refs;
- unresolved unknown;
- requested transition;
- authority/claim boundary.

Persist the context pack with an ID.

### 6. Output
Return exactly:

```yaml
moment:
  timestamp:
  available_minutes:
  next_hard_commitment:
primary:
  goal:
  project:
  action:
  why_now:
  operator:
  chat_reference:
  context_pack_id:
  first_physical_action:
  stop_condition:
  receipt_required:
  timebox_minutes:
interruption_lane:
  condition:
  operator:
  action:
waiting: []
suppressed: []
re_evaluate_when: []
```

### 7. CLI
Provide a minimal command such as:

```bash
li now --available-minutes 60
```

It must work from a fresh process against fixture/local persisted state.

No UI required.

### 8. Tests
At minimum:
- chooses one primary from 3 competing items;
- urgent inbound external reply preempts planned work;
- waiting-on-external item is not repeatedly selected;
- insufficient available time excludes oversized task;
- completed item never resurfaces;
- stale evidence lowers/blocks unsupported selection;
- failed execution routes to recovery/diagnosis;
- no invented candidate/context refs;
- deterministic rerun produces same result for unchanged state;
- context pack contains only relevant references.

## Explicitly out of scope
- dashboard;
- calendar UI;
- notifications;
- browser automation;
- sending messages;
- autonomous external writes;
- vector DB;
- graph DB;
- agent swarm;
- universal ontology expansion;
- automatic modification of priority policy from user feedback.

## Acceptance

From a fresh process with persisted fixtures representing at least three competing obligations, `li now` must return one primary action, one optional interruption lane, the exact operator, an addressable minimal context pack, stop condition, receipt, and inspectable suppression reasons.

Then mutate the fixture with an urgent external reply and prove the router deterministically changes the recommendation to that reply-handling action.

Stop there.

At completion report:

IMPLEMENTED:
TESTED:
NEGATIVE TESTS:
SAMPLE `li now` OUTPUT:
UNPROVEN:
NEXT LIVE INTEGRATION:
