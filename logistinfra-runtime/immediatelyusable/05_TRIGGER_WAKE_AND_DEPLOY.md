# Step 05 — Wake Loop + Deployment

Act as Claude Code on branch `immediatelyusable`.

Prerequisites: Steps 01–04 green.

## Objective

Make the runtime reachable and event-driven without adding another orchestration system.

Use:
- Supabase = canonical state
- Trigger.dev = durable background/wake work
- existing Node/TypeScript service = MCP + health + event endpoint
- existing connector fabric = source access

## Trigger.dev responsibilities only

- ingest signed/bounded events;
- normalize;
- SYNC affected state;
- recompute route;
- compare previous vs new primary route;
- emit a wake event only if the route materially changes;
- run safe reconcile/read retries.

Trigger.dev must NOT become canonical state.

## Deploy

Deploy the stateless service to the simplest existing Node-compatible hosting surface available in the environment.

Required endpoints:
- MCP Streamable HTTP
- health
- event/trigger ingress

Required env:
- Supabase URL/key
- Trigger.dev key/config
- connector auth/config
- service base URL

No local persistent files.

## Material-change rule

Do not notify/wake when:
- only metadata changed;
- waiting state remains waiting;
- primary route remains materially identical.

Wake when:
- external actor replies;
- approval arrives;
- blocker clears;
- deadline preempts;
- production failure preempts;
- current primary becomes invalid;
- higher-priority transition becomes admissible.

## Acceptance

1. deploy;
2. fresh remote MCP client connects;
3. create/receive one bounded test event;
4. Trigger task runs;
5. canonical state updates;
6. route changes;
7. exactly one wake payload is emitted;
8. replay event creates no duplicate wake/state effect.

## Negative tests

- invalid signature;
- duplicate webhook;
- Trigger retry;
- connector failure;
- Supabase unavailable;
- event that does not change route.

## Return

```text
DEPLOYMENT_URL:
HEALTH:
MCP:
TRIGGER_TASK:
WAKE_TEST:
DUPLICATE_TEST:
PROVES:
DOES_NOT_PROVE:
NEXT:
```

Stop once the remote runtime wakes correctly from one real/bounded event.
