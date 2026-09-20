# Step 03 — Live Read Bindings

Act as Claude Code on branch `immediatelyusable`.

Prerequisites: Steps 01–02 green.

## Objective

Bind the minimum live external reads needed for Logistinfra to stop relying on manually seeded reality.

Priority:
1. GitHub
2. Gmail
3. Google Calendar

Prefer existing external MCP/API/connector infrastructure. Do not build OAuth flows if Composio/direct managed auth can supply the surface.

## Build

Define one narrow observation interface:

```ts
interface SourceObservation {
  id: string
  source: string
  observedAt: string
  subject: string
  type: string
  payload: unknown
  sourceRef: string
  contentHash: string
}
```

Add adapters that:
- fetch bounded new/changed items;
- preserve provider IDs;
- preserve source URLs/refs;
- hash canonical payloads;
- avoid duplicate ingestion;
- emit normalized observations;
- feed only affected workstreams into SYNC/reconciliation.

Do not build a universal ETL platform.

## Minimum live queries

GitHub:
- current PR #14/head/CI;
- issue/review/reply changes relevant to registered workstreams.

Gmail:
- inbound replies;
- delivery failures;
- sent-message verification candidates.

Calendar:
- hard commitments inside a bounded near-term window.

## Acceptance

Fresh process:
1. fetch all three sources;
2. create normalized observations;
3. rerun immediately;
4. create zero duplicate observations;
5. mutate/observe one test source;
6. ingest only the delta.

## Negative tests

- provider unavailable;
- stale cursor;
- duplicate event;
- deleted/changed source;
- malformed provider response;
- auth failure.

## Return

```text
LIVE_SOURCES:
NORMALIZED_EVENT_COUNT:
IDEMPOTENCY:
AUTH_SURFACE:
TESTS:
PROVES:
DOES_NOT_PROVE:
NEXT:
```

Stop when live reads update canonical reality without duplicate state.
