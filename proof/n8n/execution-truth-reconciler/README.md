# n8n Execution Truth Reconciler

## Target

n8n issue #38396:
https://github.com/n8n-io/n8n/issues/38396

Reported operator failure:

```text
Node process fatally crashes
→ Docker restarts container
→ startup log reports unfinished executions
→ UI still shows those executions as RUNNING for ~45–50 minutes
```

The core diagnostic distinction is:

> declared execution status is not the same thing as independently supported execution truth.

## Artifact

`analyzer.py` reconciles a UI execution record against supplied process/restart evidence.

It classifies:

- `STALE_RUNNING_CONFIRMED`
- `RUNNING_NEEDS_RECONCILIATION`
- `RUNNING_NOT_DISPROVEN`
- `NON_RUNNING_STATE`

## Strongest receipt

A RUNNING execution should be considered stale when either:

1. the owning process is known dead, or
2. the execution is explicitly reported as unfinished after a process restart and its ownership belongs to the prior process lifetime.

That is stronger evidence than "the timer is still increasing."

## Useful runtime contract

A production execution-state model can separate:

```text
DECLARED_STATUS
+
PROCESS_OWNERSHIP
+
HEARTBEAT / LAST PROGRESS
+
RESTART GENERATION
+
UNFINISHED-ON-RESTART SIGNAL
→ EXECUTION TRUTH CLASSIFICATION
```

## Hostile tests

The tests prove the diagnostic does not collapse these cases:

1. RUNNING + dead process → stale confirmed
2. RUNNING + unfinished across restart → stale confirmed
3. RUNNING + stale progress + unknown process → reconciliation needed
4. RUNNING + live process + fresh progress → not disproven

## Preproof contract

```yaml
claim: detect when a declared RUNNING state conflicts with process/restart evidence
failure_case: UI continues to display RUNNING after the execution-owning process died
input_fixture: execution status + process lifetime + restart/unfinished evidence
expected_behavior: stale running state is explicitly classified
hostile_test: dead process vs unknown process vs live process
receipt: deterministic classification with reason
independent_reproduction: pytest tests/test_n8n_execution_truth_reconciler.py
claim_ceiling_before: diagnostic artifact
claim_ceiling_after_tests: deterministic state-reconciliation proof
next_external_test: use actual execution IDs + restart timestamp from #38396
```

## Claim boundary

This artifact does **not** diagnose the OOM root cause.

It isolates a second operational problem in the report: a stale execution state can remain presented as live after process death.

That can be tested independently of the memory-growth defect.
