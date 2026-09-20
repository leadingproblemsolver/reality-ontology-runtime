# CogniTimeExec NOW — Structuralized Child Contract

Priority: P0
Parent: `operational-reality-v1`

## PURPOSE
Continuously compile canonical reality into the single best executable 0–10 minute action, with an exact fallback when blocked.

## INVOKE_WHEN
- user asks `NOW`;
- current transition settles/fails/blocks;
- wake event materially changes priority;
- hard deadline enters action window;
- 10-minute block expires;
- maintenance preemption becomes material.

## INPUTS
- active/waiting/blocked workstreams;
- eligible transitions;
- commitments/deadlines;
- leverage-firewall dispositions;
- surface/auth health;
- predictive-prep status;
- maintenance alerts;
- last verified receipt;
- human availability/authority constraints.

## RULES
1. Apply hard preemption gates from Moment Router.
2. Exclude waiting/blocked/inadmissible work.
3. Exclude KILL/AUTOMATE/DELEGATE work from the user's active queue.
4. Prefer externally consequential, dependency-unlocking, compounding transitions.
5. Compile the winner into one physical/digital action that fits <=10 minutes.
6. If the transition is larger, emit only its first independently completable state change.
7. Always include stop condition + receipt + fallback.
8. Never output vague project-level work.

## OUTPUT
```yaml
moment:
  workstream:
  transition:
  why_now:
  horizon_minutes: 10
  exact_action:
  surface:
  operator:
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

## TOOLS
Reuse:
- Moment Router;
- canonical Reality Ontology state;
- Surface Registry;
- connected tools/APIs;
- Trigger.dev wake events;
- Calendar/time inputs.

No new task manager.

## MVE
Implement `compileMoment(contextPacket, operationalState)` over the existing router output.

Support four scenarios first:
1. executable external action;
2. human approval required;
3. waiting primary -> fallback;
4. maintenance/deadline preemption.

## ACCEPTANCE
- every result is startable immediately;
- no waiting item is returned as active;
- no <=1x non-essential manual task is returned;
- exact surface and receipt are present;
- same state produces deterministic admissibility;
- state change causes recomputation rather than continuation by inertia.

## FAILURE
If no useful transition exists:
return `IDLE_WITH_REASON` plus the highest-value safe PREP action, not invented busywork.

## AUTHORITY
This branch selects/compiles work. It does not redefine truth, Market Router economics, or execution authority.

## HANDOFF
- missing setup -> `or/predictive-setup`
- low-leverage labour -> `or/leverage-firewall`
- degradation -> `or/predictive-maintenance`
- recurring mandatory life overhead -> `or/life-logistics-floor`
- noise/interruption -> `or/attention-firewall`

## FIRST RECEIPT
A fresh `NOW` call produces an exact 10-minute action; after its receipt settles, a second `NOW` routes a different valid action without reconstruction.
