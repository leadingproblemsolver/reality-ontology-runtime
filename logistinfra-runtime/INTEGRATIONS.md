# Integration Map

## Phase 1 — wire now

### GitHub
Purpose: acquire live issues, preserve source URLs/IDs, later inspect commits/PRs and receipts.
Authority: READ automatically. WRITE only after explicit human approval.

### Trigger.dev
Purpose: schedules, durable background runs, retries, concurrency, task history.
Trigger: hourly scan plus manual investigation-preparation task.

### Supabase / Postgres
Purpose: canonical state.
Minimum tables: `goals`, `signals`, `opportunities`, `executions`, `evidence`, `approvals`.

### LLM provider
Purpose: only score/interpret already-filtered signals and prepare bounded investigation context.
Must return structured output. Invalid output is a persisted failure, not guessed into shape.

## Phase 2 — only after Phase 1 is verified

### Browser Use / Playwright
Purpose: perform bounded browser actions behind prepare -> approval -> execute -> fresh observe -> verify.
Never trust library action success as external-state proof.

### Gmail
Purpose: ingest replies and later send explicitly approved messages.

### LinkedIn / X / Reddit / company sites
Purpose: market signals and later externalization surfaces.
Prefer APIs/feeds/search when available; browser adapter only where necessary.

### Apollo / CRM
Purpose: enrichment and CRM side effects after live market loops justify them.

## Universal adapter contract
Every consequential adapter must expose:
1. prepare(input)
2. preconditions()
3. required_authority
4. execute(approved_payload)
5. observe_fresh_state()
6. verify(expected_transition)
7. evidence_receipt()
8. rollback_or_reconciliation_path when applicable
