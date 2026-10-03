# Moment Router — 20 Minute Activation

## Goal
Get one tangible answer from Logistinfra:

> Given what is true right now, what is the single highest-value action I should execute, which operator/chat owns it, and what receipt ends the block?

## 0–5 min — pull and run

```bash
git fetch origin
git checkout feat/logistinfra-runtime-v1
cd logistinfra-runtime
python moment_router.py reality.example.json --available-minutes 45
```

Expected: one `primary`, one `interruption_lane`, waiting items, and suppressed alternatives.

## 5–10 min — replace fixture with today's reality

Copy `reality.example.json` to `reality.today.json`.

Put only 3–7 currently plausible actions into `candidates`.

Each candidate must contain:

```json
{
  "goal": "...",
  "project": "...",
  "action": "...",
  "why_now": "...",
  "operator": "exact chat/operator",
  "chat_reference": "exact chat title if still chat-backed",
  "context_refs": ["repo/file/url/message"],
  "first_physical_action": "...",
  "stop_condition": "...",
  "receipt_required": "...",
  "timebox_minutes": 30,
  "status": "active",
  "scores": {
    "external_consequence": 0,
    "information_gain": 0,
    "deadline_pressure": 0,
    "dependency_unlock": 0,
    "relationship_access_value": 0,
    "proof_gain": 0,
    "probability_now": 0,
    "compounding_value": 0,
    "switching_cost": 0,
    "execution_cost": 0,
    "reversibility_risk": 0,
    "speculation_penalty": 0
  }
}
```

Use scores 0–10. Do not optimize them; rough relative values are sufficient.

Statuses supported now:
- `active`
- `waiting_external`
- `done`
- `cancelled`
- `rejected`

Optional `hard_gate` values:
- `safety_security`
- `external_actor_waiting`
- `deadline_window`
- `live_user_blocker`
- `approved_time_sensitive`

## 10–12 min — run today's route

```bash
python moment_router.py reality.today.json --available-minutes 45
```

Do not debate the output unless a fact is wrong.

## 12–17 min — execute the returned FIRST ACTION

Open only the returned `chat_reference` / `operator` and load only `context_refs`.

Work until `stop_condition` is met.

Capture `receipt_required`.

## 17–20 min — settle and reroute

Update the candidate:
- `done` if receipt achieved;
- `waiting_external` if another actor now owns the next move;
- keep `active` only if the block is genuinely incomplete;
- add the new external event as a candidate with a hard gate if it deserves preemption.

Run again:

```bash
python moment_router.py reality.today.json --available-minutes 30
```

That second output is the next block.

## Hostile tests

```bash
python -m pytest -q test_moment_router.py
```

Proves v0 behavior for:
1. bounded high-value action selection;
2. waiting-on-external suppression;
3. urgent external actor preemption.

## GitHub Actions

Run **Moment Router Smoke** manually from Actions or let PR changes trigger it.
It uploads `moment-router-output.json` as the routing receipt.

## Stop condition for v0

Do not add UI, LLM ranking, Supabase, calendar, email, or browser automation until this manual-state version correctly routes at least three real blocks.

After three correct real routes, automate input acquisition in this order:
1. GitHub state;
2. calendar/deadlines;
3. executions/evidence state;
4. email/replies;
5. market/job signals.
