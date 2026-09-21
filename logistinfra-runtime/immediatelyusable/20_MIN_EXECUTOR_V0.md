# LOGISTINFRA 20-MINUTE EXECUTOR V0

Goal: get one universal execution spine running NOW using existing runtime code and existing connected tools.

Do not deploy first. Do not add Supabase, MCP, Trigger.dev, browser fleet, UI, or new ontology before the first real task executes and verifies.

## User contract

Input:
```text
DO <mission>
```

Optional:
```text
CONTEXT <refs>
CONSTRAINTS <time/authority/deadline>
```

Output:
```text
NOW
WHY
SURFACE
FIRST ACTION
DONE WHEN
RECEIPT
STATUS
```

## Runtime spine

```text
TASK
→ reconstruct minimum current reality
→ compile TaskEnvelope
→ route to one admissible transition
→ compile SurfaceActionPacket
→ choose existing executor
→ execute
→ fresh external observe
→ verify
→ receipt
→ settle
→ return next action
```

## TaskEnvelope

```ts
type TaskEnvelope = {
  id: string;
  mission: string;
  objective: string;
  contextRefs: string[];
  constraints: string[];
  authority: "read" | "reversible_write" | "consequential_write" | "human_only";
  doneWhen: string;
  receiptRequired: string;
};
```

## SurfaceActionPacket

```ts
type SurfaceActionPacket = {
  taskId: string;
  workstreamId: string;
  transitionId: string;
  surface: string;
  entrypoint?: string;
  executionMode: "connector" | "api" | "cli" | "browser" | "human";
  toolRef: string;
  exactAction: string;
  payload?: unknown;
  contextRefs: string[];
  authority: TaskEnvelope["authority"];
  doneWhen: string;
  verifyWith: string;
  receiptRequired: string;
  fallback?: string;
};
```

## Executor resolution

Use exactly this order:

1. already-connected ChatGPT connector/tool
2. direct API/MCP already available
3. existing repo/CLI script
4. Claude Code for bounded implementation/repo task
5. browser/computer-use surface for unsupported websites
6. human only for credentials, irreversible judgment, physical actions

Never create a new integration if an existing one can perform the transition.

## Required V0 functions

Reuse existing:
- `sync()`
- `route()`
- `runAutonomousCycle()`
- `settle()`

Add only:

```ts
compileTaskEnvelope(input)
compileSurfaceActionPacket(context, task)
resolveExecutor(packet, registry)
runTask(input, registry, approvals)
```

`runTask` must:
1. compile task;
2. route;
3. compile packet;
4. resolve executor;
5. execute if authority permits;
6. independently verify;
7. settle only if verified;
8. return next context.

## V0 executor registry

Seed only executors already available now:

```ts
{
  "tool:github": connectorAdapter,
  "tool:gmail": connectorAdapter,
  "tool:calendar": connectorAdapter,
  "tool:hubspot": readOrApprovedWriteAdapter,
  "tool:claude-code": handoffAdapter,
  "tool:browser": browserHandoffAdapter,
  "tool:human": humanBoundaryAdapter
}
```

Do not build provider-specific frameworks.

## Context reconstruction rule

For every task retrieve only:

- current objective/workstream;
- last verified transition + receipt;
- unresolved blocker/wait;
- relevant chat/operator;
- exact artifact/repo/file;
- relevant live external state;
- frozen decisions;
- authority boundary.

No full-chat dump.

If no workstream exists, create one ephemeral task workstream with exactly one transition. Promote it to persistent state only if it becomes recurring/strategic.

## 20-minute implementation order

### Minute 0-3
Read existing:
- continuity engine
- autonomy engine
- tool adapter types
- live bootstrap state
- Surface Action Packet example

Do not redesign.

### Minute 3-8
Implement:
- `TaskEnvelope`
- `compileSurfaceActionPacket`
- `resolveExecutor`
- `runTask`

### Minute 8-12
Register ONE real adapter using the easiest current surface:
GitHub read/reversible fixture.

Acceptance:
- task routes;
- executes;
- fresh read verifies;
- receipt settles.

### Minute 12-16
Add current ChatGPT/bootstrap connector registry metadata for:
GitHub, Gmail, Calendar, HubSpot, Claude Code/browser/human handoff.

Do not implement all adapters. Unsupported executor returns exact handoff rather than failing vaguely.

### Minute 16-20
Run ONE real task end-to-end from natural language.

Example:
```text
DO inspect PR #14 current CI state and tell me the first blocking failure; if no failure, settle that CI is green and route the next runtime task
```

Must produce:
```text
TASK
→ CONTEXT
→ ROUTE
→ EXECUTE
→ VERIFY
→ RECEIPT
→ SETTLE
→ NEXT
```

## Hard V0 acceptance

Call V0 WORKING when:

- natural-language task enters once;
- minimum context is reconstructed;
- one executor is selected automatically;
- action occurs or cleanly stops at a human/authority boundary;
- outcome is freshly observed;
- success is never inferred from tool return alone;
- verified receipt is stored;
- next action is returned without the user reconstructing context.

## Explicitly defer

Until this first loop works:
- Supabase migration
- remote MCP service
- Trigger.dev
- predictive setup
- predictive maintenance
- life-logistics floor
- attention firewall
- leverage scoring
- marketplaces
- startup packaging
- broad browser automation
- universal connector framework

Those attach AFTER the execution spine works.

## 48-hour startup expansion

Once V0 works, productize only the proved primitive:

```text
"Give Logistinfra a digital task.
It reconstructs only relevant context,
chooses the execution surface,
acts through existing tools,
verifies reality,
and returns the next state."
```

Then add:
1. remote MCP/API;
2. persistent Supabase state;
3. browser executor;
4. Trigger.dev wake/event loop;
5. predictive prep/maintenance;
6. plugin/marketplace distribution.

No broader build before external use.
