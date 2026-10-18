# n8n Retry-Safe Webhook Reference

## Problem

Webhook senders retry. n8n executions can also duplicate, overlap, time out, or fail after an external side effect.

The dangerous pattern is:

```text
webhook → side effect
```

because neither a green execution nor an n8n execution ID proves that a business event was processed exactly once.

## Invariant

Use the **provider/business event ID** as the idempotency key when one exists.

Then enforce:

```text
event_key
→ atomic claim
→ PROCESSING
→ external side effect
→ durable external receipt
→ COMPLETED
```

Duplicates must never blindly re-run the side effect.

## State machine

```text
NEW
 └─ atomic claim succeeds → PROCESSING
       ├─ side effect + receipt → COMPLETED
       └─ no verified receipt / failure → FAILED
             └─ explicit retry → PROCESSING

duplicate while PROCESSING
→ SUPPRESS / WAIT / RECONCILE

duplicate after COMPLETED
→ RETURN EXISTING RECEIPT
```

## Why an n8n execution ID is not enough

An execution ID identifies an n8n run. A retried webhook delivery can create another execution for the **same business event**.

Idempotency belongs to the business event or side-effect object.

## Included proof artifacts

- `idempotent_webhook.py` — tiny executable model of the state contract.
- `schema.postgres.sql` — Postgres version suitable for an n8n Postgres node.
- `../../../tests/test_n8n_idempotent_webhook.py` — hostile tests.

The tests prove:

1. three deliveries of one event cause one side effect;
2. a failed first attempt can retry under the same event identity;
3. an in-flight duplicate is suppressed;
4. eight simultaneous claims produce exactly one executor.

## n8n reference workflow

Build the workflow as:

```text
Webhook
→ Extract stable event_key
→ Postgres: INSERT ... ON CONFLICT DO NOTHING RETURNING ...
→ IF claim returned a row?
   YES → perform side effect
        → require externally inspectable receipt
        → Postgres: mark COMPLETED + receipt
        → respond success
   NO  → Postgres: read existing state
        → COMPLETED: return prior receipt
        → PROCESSING: suppress / 202 / retry later
        → FAILED: explicitly reacquire for retry, then continue
```

### Important

Do not blindly retry a side-effecting node after an ambiguous timeout.

If the remote system may have accepted the mutation, **reread the remote target using the business key before retrying**.

That is the difference between retry logic and safe recovery.

## Preproof contract

```yaml
claim: duplicate delivery does not create duplicate side effects
failure_case: same event arrives concurrently and/or is retried after failure
input_fixture: one stable event_key delivered repeatedly
expected_behavior: one active executor per event_key
hostile_test: 8 concurrent claim attempts
receipt: externally inspectable side-effect identifier persisted with COMPLETED
independent_reproduction: pytest tests/test_n8n_idempotent_webhook.py
claim_ceiling_before: reference implementation
claim_ceiling_after_tests: deterministic local proof of the state machine
next_external_test: reproduce in an actual n8n workflow with Postgres and a visible side effect
```

## Claim boundary

This artifact does **not** prove that n8n itself never duplicates webhook executions.

It proves a workflow-level contract that prevents duplicate business side effects even when duplicate delivery/execution occurs.
