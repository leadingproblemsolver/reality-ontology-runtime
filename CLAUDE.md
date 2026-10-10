# Claude Code — Logistinfra / Reality Ontology

**Operate the existing system. No replacement architecture.**

## One authority
- Local canonical state: Python `RealityStore` in `src/reality_ontology/store.py`, ontology contracts in `ontology/`, persisted in `.runtime/reality.db` or explicit `RO_DB`.
- The TypeScript `logistinfra-runtime/src/continuity/*` JSON store and its Supabase opportunity store are **not reconciled** to that Python ledger. Treat as scoped projections/independent workloads. Never claim both are one authoritative state system.
- Models, planned sends, rendered artifacts, CI and tool success do NOT constitute independently verified external results.
- Never promote a claim, approve a consequential mutation, or settle an external effect without appropriate authority, independent verification, and provenance.
- Operate only Taha's Logistinfra/workstreams. Do not import unrelated shared-account history.

## Automatic session activation
Project `.claude/settings.json` invokes `scripts/claude_session_context.py` at SessionStart. It READS (not creates/updates) local canonical DB and injects a factual context summary. It does **not** sync live connector sources or schedule unattended workflows. Do not mistake presence of Claude instructions for operational automation.

## Standard control surface
Use project skill `/operate NOW`, `/operate CONTINUE <workstream>`, `/operate PREP`, `/operate EXECUTE`, `/operate WATCH`, or `/operate SETTLE`.

Before each transition: inspect verified observations, dependencies, approval, exact source and receipt. Run the smallest action with greatest external consequence. After: fresh-verify, settle to ONE authority, restart to reconstruct. Block or kill rather than invent completion.

## Verified existing entrypoints
- `python -m reality_ontology.cli --db .runtime/reality.db init` — initialize local ledger.
- `python -m reality_ontology.cli --db .runtime/reality.db verify-invariants` — current ledger invariant report.
- `python -m reality_ontology.cli --db .runtime/reality.db next` — current mission; error if none exists is honest.
- `python -m reality_ontology.cli --db .runtime/reality.db next-start --spec <evidence-backed.json>` — one selected mission.
- `python -m reality_ontology.cli --db .runtime/reality.db next-settle RECEIPT --observation "<truth>" --receipt "<inspected-locator>"` — receipt settlement; verify before executing.
- `python -m pytest` — core Python tests.
- `cd logistinfra-runtime && npm ci && npm run build && npm test` — existing TS slice and tests. TS continuity output remains noncanonical until adapter reconciliation.

## Relevant existing assets
- `logistinfra-runtime/bootstrap/continuity.live.v0.json`: 2026-09-20 seed, not live truth.
- `logistinfra-runtime/bootstrap/surfaces.v0.json`: candidate connector registry, not Claude auth confirmation.
- `logistinfra-runtime/src/pipelines/github_opportunity/`: scheduled GitHub scouting slice.
- `logistinfra-runtime/operational-reality/CLAUDE_EXECUTION_PACKET.md`: integration backlog.
- `logistinfra-runtime/operational-reality/OPERATIONAL_REALITY_CONTRACT.md`: operations acceptance.
- `logistinfra-runtime/DEPLOYMENT_MINIMUM_V1.md`: known missing standalone seams.
- `docs/CLAUDE_LOCAL_CUTOVER.md`: exact migration gates and local activation.

## Safety and closure
External sends, calls, publications, commits into third-party projects, money and destructive changes require user approval. Source-specific policy and DNC restrictions still apply. Fresh external re-read is mandatory when available. Never automatically transfer ChatGPT private chats; only import user-authorized exports with hashes and source locators. No unattended cloud writes until canonical remote persistence, signed triggers and replay-safe approval/verification pass.

Per execution return: observed before → actual operation/tool → independent receipt or failure → updated canonical state → next external transition.
