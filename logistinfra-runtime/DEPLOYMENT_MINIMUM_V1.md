# Logistinfra Minimum Deployable V1

## Status

The kernel is usable today through:
- local CLI / fixture state;
- this ChatGPT control plane with live connected GitHub/Gmail/Calendar/HubSpot reads;
- tested continuity, routing, autonomy, approval, verification and settlement logic.

It is NOT yet a standalone persistent deployment because four runtime seams remain:
1. durable canonical store adapter;
2. network/MCP facade;
3. standalone connector/event binding;
4. real execute+verify adapters.

Do not widen scope before the first real closed loop.

## Chosen minimum stack

### Canonical state
Supabase/Postgres.

Implement `SupabaseContinuityStore` behind the existing `ContinuityStore` interface.
Reuse existing migrations.
Do not create a new state model.

### Logistinfra tool surface
Official TypeScript MCP SDK over Streamable HTTP.

Expose only:
- now
- sync
- continue
- prep
- execute
- watch
- settle
- search_workstreams
- search_chats
- record_feedback

Reuse existing continuity/autonomy code.
Do not introduce a Python MCP service solely for FastMCP.

### External tools/auth
Primary: Composio session/Connect MCP or direct official APIs where simpler.

The client may connect independently to:
- Logistinfra MCP — truth/routing/settlement
- external integration MCP — Gmail/GitHub/Calendar/HubSpot actions

Do not proxy the external tool catalog through Logistinfra.

During bootstrap, ChatGPT's existing connectors remain a valid operator/control surface.

### Background execution / wake
Trigger.dev.

The dependency already exists in `logistinfra-runtime/package.json`.

Use only for:
- signed external event ingestion;
- bounded background SYNC;
- retryable read/reconcile work;
- priority-delta calculation;
- wake delivery.

Do NOT let Trigger.dev define canonical workstream state.
Do NOT build another queue.

### First real adapters
1. GitHub
2. Gmail

Each must implement:
- execute
- fresh independent verify

Do not add Calendar writes, HubSpot writes, Slack writes, browser automation or broad CRM support until the first loop passes.

### Deployment
Deploy the stateless HTTP/MCP/event service to an existing simple Node hosting surface (Vercel/Railway/Render acceptable).

All durable state must live in Supabase.
All long-running/retryable work must live in Trigger.dev.
No local filesystem state in production.

### User shell
NOT a blocker.

V1 may be used from:
- Claude Code / another MCP client;
- current ChatGPT bootstrap control plane;
- later LibreChat.

LibreChat becomes useful after the runtime passes the live receipt test; its UI is not required to prove the runtime.

## Explicitly deferred

### Firecrawl
Useful as a hosted web-source adapter for market/research operators after the core loop.
Do not self-host initially.

### Instructor
Not needed in the TypeScript control plane; current code already uses Zod.
Use only inside a Python extraction worker if a concrete extraction lane benefits.

### n8n
Use for client-specific CRM/workflow delivery where its nodes materially reduce setup.
Do not make it the canonical Logistinfra runtime or state machine.

### FastMCP
Good option for Python services, but current core is TypeScript.
Use official TS MCP SDK unless a Python worker independently needs MCP.

### LibreChat
User-facing shell after first closed loop.

### Browser automation
Add only for surfaces without stable API/MCP coverage.

## Exact implementation sequence

1. Supabase store
   - implement store adapter;
   - seed bootstrap workstreams;
   - fresh-process read/write test.

2. MCP facade
   - expose NOW/CONTINUE/PREP/WATCH/SETTLE and core routing tools;
   - no duplicate business logic;
   - standard Streamable HTTP endpoint.

3. Connector binding
   - connect GitHub/Gmail/Calendar read surfaces through Composio/direct APIs;
   - normalize observations into SOURCE_EVENT shape;
   - idempotent ingestion.

4. GitHub execute+verify
   - approved issue comment as first consequential write;
   - fresh comments read verifies exact single effect.

5. Gmail execute+verify
   - approved draft/send fixture;
   - fresh Sent/thread read verifies effect.

6. Trigger.dev wake
   - external event -> normalize -> SYNC -> route-delta;
   - wake only when primary route materially changes.

7. Deploy
   - MCP/event HTTP service;
   - Supabase env;
   - Trigger.dev env;
   - connector credentials;
   - health check.

8. Live closed-loop acceptance
   - ingest live external event;
   - NOW selects correct transition;
   - PREP creates exact action packet;
   - consequential EXECUTE pauses for approval;
   - after approval, action executes once;
   - fresh external read verifies;
   - SETTLE persists receipt;
   - fresh client/session NOW advances to next transition.

## Production acceptance gate

Do not call the runtime deployed/usable standalone until all are true:

- [ ] Supabase is canonical and survives restart
- [ ] MCP endpoint responds from a fresh client
- [ ] at least GitHub/Gmail live reads work standalone
- [ ] approval gate works
- [ ] GitHub real write is verified independently
- [ ] SETTLE persists receipt
- [ ] restart/fresh session does not repeat settled action
- [ ] one wake event materially changes route
- [ ] waiting work remains suppressed
- [ ] current route advances automatically after settlement

## First real receipt

Use the prepared LangGraph #8464 Surface Action Packet only after explicit user approval.

Expected loop:
`PREPARED -> APPROVED -> GitHub comment -> fresh issue reread -> exactly one matching comment -> SETTLE -> WAIT`

This proves the first real user-facing executable surface without expanding scope.

## Stop condition

After the first live loop passes:
STOP CORE INFRA BUILD.

Then add one missing capability only when a real workstream demands it:
- Firecrawl web signal source;
- HubSpot write;
- browser executor;
- LibreChat shell;
- n8n customer workflow;
- eval/observability expansion.
