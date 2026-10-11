# Claude Code local cutover — runbook and acceptance

## Observed baseline (October 10, 2026)
- Repository: `leadingproblemsolver/reality-ontology-runtime`.
- Base: `operational-reality-v1`, commit `4134effc6950a9b6afdb16ab02bbdb19877a6bc0`; latest GitHub CI successful.
- `main` contains the Python ontology runtime but not the consolidated Logistinfra TS tree.
- PR #14 remains draft; PR #16 remains open. Do not blindly merge branches with overlapping control planes.
- Existing: Python durable ledger, NextMove, TS continuity/autonomy, Supabase opportunity adapter, GitHub scouting scheduler, CI, Claude prompt contracts and surface seed.
- Not proven: standalone portable GitHub/Gmail/Calendar source reads into ONE canonical ledger; Claude MCP facade; reconciliation of Python SQLite and TS JSON/Supabase; approved GitHub/Gmail execute → external reread → settlement; live session/restart wake.
- ChatGPT conversations are not automatically accessible to Claude. Import only user-authorized exports with identity, source, timestamp, hashes and deduplication.

## Minimum operator bootstrap (after cloning, Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-claude.ps1
```

This initializes only the local canonical SQLite ledger, runs Python invariants/tests, prints the read-only session context, then launches Claude Code. Use `-VerifyTypeScript` to additionally execute the existing TypeScript build/tests; `-NoLaunch` to verify without opening Claude. It does NOT bind cloud credentials, ingest all chats, or authorize external mutations.

## Windows local setup (one-time)

Prerequisites: Git, Python 3.11+, Node 20+, Claude Code CLI, authentication to specific services only when needed.

```powershell
git clone --branch feat/claude-local-activation-v1 https://github.com/leadingproblemsolver/reality-ontology-runtime.git
cd reality-ontology-runtime
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m reality_ontology.cli --db .runtime/reality.db init
python -m reality_ontology.cli --db .runtime/reality.db verify-invariants
python scripts/claude_session_context.py
claude
```

Within Claude Code run `/operate NOW`. On a new empty ledger, it must return uninitialized rather than fabricate a live workstream. Seed one REAL observed mission from an external source before any settlement.

To verify the TypeScript slice independently:
```powershell
cd logistinfra-runtime
npm ci
npm run build
npm test
```

This validates code/tests only, not production adapters.

## Dependency-correct completion sequence

| Gate | Exact execution | Required receipt |
|---|---|---|
| G0 Claude entry | Fresh Claude Code session loads `CLAUDE.md`, SessionStart and `/operate` | session trace shows correct read-only DB state; empty/corrupt DB fails closed |
| G1 One durable mission | one real `next-start` → `next` → authorized action → verified `next-settle` → fresh-process `next` | persisted event/receipt; no duplicate settlement |
| G2 Portable source | authenticate GitHub with exact Claude MCP/API permissions; reconcile observation to Python ledger, using existing adapter primitives | one fresh live GitHub read with source ID/time; replay zero duplicates; restart reconstructs |
| G3 External write | bounded, approved GitHub action → independently reread target → exactly-one side effect → canonical settlement | source URL, fresh verify, settled event, safe rerun |
| G4 Wake | reuse GitHub Actions or existing Trigger.dev after G3; schedule routes through new SYNC not cached state | one trigger changes admissible next move, one verified wake |
| G5 Expansion | audit active external lanes individually (Matthew/Bridge Builders, GateOfAI, reliability audit/n8n, technical contributions, direct-human outreach, Zynro, internships) | per-lane source/owner/action/auth/verifier/receipt; otherwise `REGISTERED_NOT_BOUND` |

Do not deploy every lane concurrently. Promote only after each live acceptance test. Market/outreach sends require specific approvals and any DNC constraints; no silent distribution.

## Authority rules
- For **local cutover**, `RealityStore` in Python is the canonical ledger. The TS continuity JSON and Supabase tables are scoped stores, not interchangeable claims about the same state.
- A migration or adapter may not claim consistency until crash/restart/replay, missing data, duplicate calls, and contradictory evidence tests pass.
- Approval state cannot be inferred from a ChatGPT/Claude conversation. Require exact authorized action and payload.
- Claude Cloud routines can later supply schedules and GitHub triggers, but are not automatically connected to the same local SQLite file. A transactional remote state store must be proven before automatic cloud mutation.

## End-state acceptance
A fresh Claude session with **no pasted history** identifies one verified workstream → picks one admissible move → uses the right authorized tool → observes external state independently → records canonical receipt → survives restart → emits the next nonduplicative action. Repeat for each migrated pipeline before claiming global activation.

## Next implementation, not another strategy document
Inspect `logistinfra-runtime/immediatelyusable/00_SERIES_INDEX.md` and `logistinfra-runtime/operational-reality/CLAUDE_EXECUTION_PACKET.md`. Implement *one* reconciliation path between the existing TS workflow and Python ledger (or prove via tests the chosen single authority), bind live GitHub reads, test replay/restart, then request approval for exactly one low-risk write. Only after a real receipt add Gmail and triggered wake.


## G2 portable source read — added on the Claude cutover branch
This is a read-only API observation adapter into Python RealityStore, not a TS JSON/Supabase reconciliation or an external-write verifier.

After installing the Python package, execute in PowerShell from the repo root:

```powershell
python -m reality_ontology.github_ingest --db .runtime/reality.db --repo leadingproblemsolver/reality-ontology-runtime --pr 17
python -m reality_ontology.github_ingest --db .runtime/reality.db --repo leadingproblemsolver/reality-ontology-runtime --pr 17
python scripts/claude_session_context.py
```

First run should return `NEW_OBSERVATION` and second should return `UNCHANGED`, with the same `event_id`. Changing the remote PR produces a *new observation*, not a promoted success claim. For private GitHub repositories supply your locally held `GITHUB_TOKEN` environment variable; never commit it.

To sync this concrete source automatically at each Claude Code start, set in the same PowerShell process before launching Claude:

```powershell
$env:RO_GITHUB_PRS = "leadingproblemsolver/reality-ontology-runtime#17"
claude
```

The SessionStart hook first reads the explicitly listed source, appends a replay-safe L0 observation, and then compiles the read-only context. At most two semicolon-separated PR targets per session. Unset `RO_GITHUB_PRS` means no live ingestion and never claims otherwise. Read errors result in `BLOCKED` for fresh-state claims; they do not authorize action based on old data.

**G2 acceptance:** Local fresh Claude session trace plus two live CLI reads and DB event/evidence identity. CI fixture tests prove deterministic replay only; a green CI run does not prove local network credentials or Claude Code session startup.

**Not migrated:** Gmail, Calendar, HubSpot, external writes/verification, cross-store TS↔Python reconciliation, and autonomous wake. Do not promote those to READY based on GitHub adapter tests.

## G3 bounded GitHub issue-comment adapter (approval required)
The code implements a narrow external comment adapter, but no live external comment has been authorized or sent by this PR. GitHub comment author identity (must equal the executing token's `GET /user` login), matching comment markers, and exact payload hashing are enforced; a byte-identical comment by another account is never accepted as the receipt. Before writing, it independently reads existing comments, and afterwards rereads to confirm exactly one matching comment. On ambiguous or failed verification, settlement is blocked.

Prepare one real target and its message (example uses local file `comment.txt`):
```powershell
python -m reality_ontology.github_comment_cli --db .runtime/reality.db --repo OWNER/REPO --issue 123 --message-file comment.txt prepare
```
Only after personally checking the target and exact message, explicitly approve that *same* file by typing the full digest-bound transition ID:
```powershell
python -m reality_ontology.github_comment_cli --db .runtime/reality.db --repo OWNER/REPO --issue 123 --message-file comment.txt approve
```
Then execute with an appropriately scoped local `GITHUB_TOKEN`:
```powershell
python -m reality_ontology.github_comment_cli --db .runtime/reality.db --repo OWNER/REPO --issue 123 --message-file comment.txt execute
```

Tests with an isolated fake API prove approval absence blocks writes, mutated payload requires new approval, a verified replay does not repost, and a write without independent verification cannot settle. This is not a declaration of G3 completion until a *real approved* comment is verified and resumed from another process.


## 2026-10-11 migration audit
See `logistinfra-runtime/bootstrap/migration_manifest.v1.json` (validated by `tests/test_migration_manifest.py`) for the per-pipeline inventory with provenance, state, blockers and exact next action, and `logistinfra-runtime/live/receipts/g1-g2-github-binding-2026-10-11.json` for the exported G1/G2 receipt. Gmail/Calendar are BLOCKED on account identity, and the first real G3 write awaits human approval of a prepared packet.
