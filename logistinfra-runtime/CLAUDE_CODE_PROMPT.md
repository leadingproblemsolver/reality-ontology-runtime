# Claude Code Prompt — Logistinfra Runtime V1

Implement only the first verified background vertical slice.

## Live workload
Continuously inspect `browser-use/browser-use` GitHub issues for bounded, reproducible reliability bugs that the repository owner can personally investigate and contribute to.

## Target closed loop
scheduled trigger -> retrieve issues -> deterministic filter -> structured LLM evaluation -> ranked opportunity -> persist state -> require human decision -> prepare bounded investigation -> record evidence

## Technology
- TypeScript inside `logistinfra-runtime/`
- Trigger.dev for scheduled/background execution
- Supabase/Postgres for canonical state
- GitHub API for issue acquisition
- one configurable LLM provider
- Vitest or equivalent

## Create
- `src/reality/`
- `src/pipelines/github_opportunity/`
- `src/adapters/`
- `src/policies/`
- `src/trigger/`
- `supabase/migrations/`
- `tests/`

## Minimum tables
`goals`, `signals`, `opportunities`, `executions`, `evidence`, `approvals`

## Implement only
1. GitHub issue acquisition for `browser-use/browser-use`.
2. Idempotent signal persistence.
3. Deterministic filtering before any LLM call.
4. Structured LLM scoring against:
   - reproducibility <=60 minutes
   - bounded scope
   - Python relevance
   - reliability/failure-semantics relevance
   - maintainer verification potential
   - setup burden
   - confidence
5. Persist ranked opportunities.
6. Scheduled Trigger.dev task.
7. Manually invokable investigation-preparation task.
8. Explicit human approval state.
9. Evidence/logging sufficient to reconstruct why an issue was selected.
10. Tests for duplicate ingestion, malformed GitHub responses, invalid LLM output, no qualifying issues, and rerun idempotency.

## Invariants
- model output is not canonical truth
- raw source/provenance is preserved
- duplicate scheduled runs do not duplicate opportunities
- no GitHub mutation occurs
- no issue is claimed/commented automatically
- human approval is mandatory before consequential external action
- failure is persisted rather than converted into success
- every recommendation references source evidence

## Success test
From a fresh process, run against live or fixture GitHub issue data and produce a persisted ranked opportunity whose source, filtering decision, score, rationale, uncertainty, and recommended next action can all be reconstructed.

Run it twice and prove no duplicate side effect occurs.

## Stop
Do not implement the browser executor, outreach, generalized multi-agent system, dashboards, vector DBs, graph DBs, or unrelated architecture.

At completion report exactly:
IMPLEMENTED:
TESTED:
NEGATIVE TESTS:
LIVE/FIXTURE RECEIPT:
UNPROVEN:
NEXT EXTERNAL ACTION:
