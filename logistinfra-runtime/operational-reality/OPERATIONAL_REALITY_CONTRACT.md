# Operational Reality Contract

Source discipline follows the structuralization pack:

`route → extract → select MVEs → bind existing tools → execute → validate → settle`

## Admission rule

A new operational object belongs in canonical state only if it can change at least one of:

- what is true;
- what is possible;
- what matters now;
- what is blocked/waiting;
- what should be prepared;
- what should be maintained;
- how an action executes;
- how completion is verified;
- when the system should wake.

Everything else is archival context.

## Core operational object

Every actionable operation uses:

```yaml
operation:
  id:
  trigger:
  input_state:
  required_context:
  actor:
  authority:
  labour:
  judgment_rules:
  tool:
  surface:
  prep_status:
  output_state:
  acceptance_test:
  evidence:
  receipt:
  wake_condition:
  fallback:
  source_refs:
```

## 10-minute Moment Contract

Every routed primary transition must compile to:

```yaml
moment:
  workstream:
  transition:
  horizon_minutes: 10
  exact_action:
  surface:
  setup_required:
  prep_status:
  authority:
  can_execute_now:
  blocked_by:
  stop_after:
  receipt_required:
  if_finished_early:
  if_blocked:
  interrupt_if:
```

No output such as "work on university", "do outreach", or "continue Logistinfra" is valid.

## Three horizons

- NOW: 0–10 minutes, executable.
- NEXT: 10–60 minutes, dependency-correct successor.
- UPCOMING: hours/days, wake conditions + reversible preparation only.

## Human attention invariant

Tool-executable labour must be delegated to existing tools when reliability is adequate.

Human attention is reserved for:
- irreversible judgment;
- trust/relationship work;
- credentials/access;
- negotiation;
- physical action;
- high-information correction.

## Settlement

Every meaningful block runs the existing compounding settlement contract and records:
- state before/after;
- actual evidence;
- labour removed;
- recurring maintenance introduced;
- next checkpoint;
- exact next action.
