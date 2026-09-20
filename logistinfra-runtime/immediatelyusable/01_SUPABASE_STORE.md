# Step 01 — Supabase Continuity Store

Act as Claude Code on branch `immediatelyusable`.

## Objective

Replace production file-backed continuity with Supabase/Postgres while preserving the current `ContinuityStore` interface and all existing semantics.

Read first:
- `src/continuity/store.ts`
- `src/continuity/engine.ts`
- `src/continuity/types.ts`
- `supabase/migrations/0002_live_context_engine.sql`
- `bootstrap/continuity.live.v0.json`
- `tests/continuity.test.ts`
- `tests/live-bootstrap.test.ts`

## Build only

Create a `SupabaseContinuityStore` implementing:
- `load(): Promise<GlobalState>`
- `save(state: GlobalState): Promise<void>`

Map only existing canonical objects:
- global_state
- chat_registry
- workstream_capsules
- continuity_transitions
- continuity_receipts

Do not invent a new schema.

Add:
- env validation for `LOGISTINFRA_SUPABASE_URL`
- env validation for `LOGISTINFRA_SUPABASE_SERVICE_ROLE_KEY`
- explicit fixture fallback only in test/dev
- seed/import command for `bootstrap/continuity.live.v0.json`

## Invariants

- duplicate receipt cannot create duplicate state;
- settled transition remains settled after restart;
- waiting work remains waiting;
- frozen decisions round-trip exactly;
- missing DB credentials must fail explicitly in production mode;
- no local JSON file is canonical in production.

## Acceptance

1. seed V0 into Supabase;
2. fresh process loads identical workstreams/transitions;
3. settle a verified fixture transition;
4. fresh process loads settled receipt and advanced workstream;
5. rerunning settlement is idempotent.

## Negative tests

- malformed state;
- unknown transition receipt;
- duplicate receipt;
- stale write/replay where applicable;
- missing env;
- partial database failure must not claim success.

## Return

```text
REUSED:
FILES_ADDED:
FILES_CHANGED:
TESTS:
PROVES:
DOES_NOT_PROVE:
MANUAL_ENV_REQUIRED:
NEXT:
```

Stop once persistence survives a fresh process.
