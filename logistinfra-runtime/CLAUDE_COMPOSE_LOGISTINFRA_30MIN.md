# Claude Code Handoff — Compose Logistinfra, Do Not Rebuild It

Repository: leadingproblemsolver/reality-ontology-runtime
Branch: feat/logistinfra-runtime-v1

## Objective

Create the smallest runnable composition that turns the existing Logistinfra kernel into a user-facing Navigator using mature external systems.

Do NOT build a bespoke chat UI, connector framework, memory system, workflow engine, agent swarm, vector DB or knowledge graph.

Read first:
- logistinfra-runtime/COMPOSITION_DECISION_2026-09-19.md
- logistinfra-runtime/CURRENT_CONNECTOR_SURFACE.md
- logistinfra-runtime/TRI_PLANE_ROLE_SPLIT.md
- logistinfra-runtime/INTEGRATION_PLANE.md
- logistinfra-runtime/MOMENT_ROUTER.md
- logistinfra-runtime/src/continuity/**
- logistinfra-runtime/tests/continuity.test.ts
- logistinfra-runtime/supabase/migrations/0001_logistinfra_runtime.sql
- logistinfra-runtime/supabase/migrations/0002_live_context_engine.sql

Use current official docs for LibreChat, MCP, Composio and the chosen SDKs before coding.

## Reuse decisions already made

- LibreChat = UX shell.
- Existing Logistinfra code = Reality/continuity/routing kernel.
- Supabase/Postgres = canonical state.
- Composio = preferred auth/integration fabric.
- Existing GitHub Actions remain scheduler for current scans.
- Langfuse is deferred until the first live closed loop unless instrumentation is trivial and cannot delay it.

## Build only these seams

### 1. Remote MCP facade over existing Logistinfra kernel

Create a small server under e.g.:
`logistinfra-runtime/src/mcp/`

Expose:
- sync
- now
- route
- context
- settle
- search_chats
- search_workstreams
- record_feedback
- prepare_handoff

Requirements:
- call existing continuity/router logic rather than duplicate it;
- structured JSON schemas;
- read tools may run automatically;
- consequential write tools must preserve approval/authority boundary;
- every state-changing result returns PROVES / DOES_NOT_PROVE;
- remote Streamable HTTP transport suitable for LibreChat;
- fixture mode when Supabase/env credentials are absent.

### 2. Chat/history ingestion seams

Create importers, not scrapers.

Required:
- ChatGPT export JSON
- Claude export JSON
- Gemini Apps Takeout input fixture/adapter
- Gemini CLI exported/shared session or documented session-store fixture
- Claude Code exported/script-interface transcript fixture

Normalize into the existing structuralization contract:
SOURCE -> PURPOSE -> INVOKE_WHEN -> INPUTS -> RULES -> TOOLS -> OUTPUTS -> ACCEPTANCE -> FAILURE -> AUTHORITY -> HANDOFF -> STALENESS

Preserve raw source refs and hashes.
Idempotent reimport.

Do not attempt live browser scraping of provider UIs.

### 3. LibreChat deployment/config bundle

Do not fork LibreChat unless unavoidable.

Add a deployment/config folder containing:
- exact Docker/Railway-ready setup notes
- example librechat.yaml
- Navigator Agent instruction file
- MCP connection config pointing at LOGISTINFRA_MCP_URL
- capabilities required: MCP/tools, code execution, artifacts, file context/search, web search, memory if configured, background calls where supported
- model-provider env placeholders only; no secrets

Navigator instruction:
- SYNC before substantive routing when state may be stale
- Reality Ontology is canonical truth
- Moment Router owns immediate transition
- Market Router owns market-facing priority
- retrieve minimum context, never dump corpus
- dynamically discover tools
- prepare/execute only within authority
- verify, then SETTLE
- show one primary move + one interruption lane

### 4. Connector bridge

Prefer Composio's MCP/session/tool-search surface.
Do NOT write Gmail/GitHub/Slack/CRM adapters if Composio or an existing direct connector covers them.

Implement only the interface seam needed for Logistinfra to:
- discover required external tool
- execute approved action
- persist external tool result as observation
- independently verify expected transition where possible

Provide a clean fallback interface for Pipedream/direct APIs.

### 5. First real corpus fixture

Use three actual high-value Market Router chat exports/files if present.
If unavailable in working tree, make the importer accept a mounted input directory and keep fixture tests representative; do not invent historical claims.

### 6. Proactive event seam

Minimum only:
external event/webhook -> SYNC -> recompute affected route -> emit priority_changed event only if route materially changes.

Do not build a notification product.
Return an event payload that can later be delivered through LibreChat Agent Events or Slack.

## Acceptance tests

A. Chat import
- duplicate import idempotent
- stable IDs
- exact source provenance
- stale copy cannot silently supersede current evidence

B. Navigator MCP
Fresh process:
- sync
- route mission
- recover chat/operator/tool/artifact/context
- settle verified fixture receipt
- new process routes next transition

C. LibreChat compatibility
- MCP server schema can be connected by a standard Streamable HTTP MCP client
- fixture client invokes now and receives one primary action
- no LibreChat source fork required

D. Market path
- selected market transition exposes required external tool/action
- unapproved consequential action is rejected
- verified receipt advances state
- tool-returned success without independent verification does NOT settle

E. Learning
- WRONG_PRIORITY feedback persists as evidence/eval candidate
- it does not automatically mutate hard policy

## Stop condition

Stop as soon as the composition is runnable end to end:
history source -> structuralize -> canonical state -> MCP now -> user-facing Navigator-compatible packet -> approved external action adapter -> verified receipt -> SETTLE -> next route.

Do not optimize architecture after that.

## Completion output

REUSED_AS_IS:
COMPOSED:
THIN_CODE_ADDED:
TESTS_PASSED:
LIVE_OR_FIXTURE_RECEIPTS:
UNPROVEN:
MANUAL_SETUP_REQUIRED:
FIRST_COMMANDS_TO_RUN:
NEXT_EXTERNAL_ACTION:
