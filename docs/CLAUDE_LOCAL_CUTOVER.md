# Claude Code local cutover — runbook and acceptance

## Observed baseline (October 10, 2026)
- Repository: `leadingproblemsolver/reality-ontology-runtime`.
- Base: `operational-reality-v1`, commit `4134effc6950a9b6afdb16ab02bbdb19877a6bc0`; latest GitHub CI successful.
- `main` contains the Python ontology runtime but not the consolidated Logistinfra TS tree.
- PR #14 remains draft; PR #16 remains open. Do not blindly merge branches with overlapping control planes.
- Existing: Python durable ledger, NextMove, TS continuity/autonomy, Supabase opportunity adapter, GitHub scouting scheduler, CI, Claude prompt contracts and surface seed.
- Not proven: standalone portable GitHub/Gmail/Calendar source reads into ONE canonical ledger; Claude MCP facade; reconciliation of Python SQLite and TS JSON/Supabase; approved GitHub/Gmail execute → external reread → settlement; live session/restart wake.
- ChatGPT conversations are not automatically accessible to Claude. Import only user-authorized exports with identity, source, timestamp, hashes and deduplication.

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
