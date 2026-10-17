# Logistinfra Integration Plane

## Purpose

Gemini owns integration discovery, connection, ingestion, normalization, synchronization, and routing across external systems. Claude/production chats own implementation, hardening, testing, deployment, and productization once a production change is selected.

The context problem should be solved primarily as an integration/data problem, not by manual chat navigation.

## Division of labor

### Gemini = Integration Plane
Gemini should:
- discover usable APIs/connectors/repos/tools;
- connect existing systems before building new ones;
- ingest chats, files, GitHub, calendar, email, market/job sources, and other relevant systems;
- normalize each source into stable typed records;
- preserve provenance and freshness;
- maintain current state automatically;
- route to the correct prior chat/operator/artifact;
- compile minimum context bundles;
- identify missing integrations/credentials;
- create fixtures and adapter contracts when live credentials are unavailable;
- hand off production work as explicit contracts.

### Claude / production chats = Production Plane
Claude should:
- consume an explicit handoff contract;
- modify code/config/infrastructure;
- run tests and hostile tests;
- deploy;
- verify the result;
- return receipts and changed state;
- stop when acceptance criteria are met.

Gemini should not become the primary code-production environment when a production chat/Claude Code already owns that surface.

## Context automation pipeline

```text
SOURCES
  Chat exports / structuralization pack
  GitHub
  Calendar
  Gmail
  files/docs
  market/job sources
  browser events
  external receipts
        ↓
INGESTION ADAPTERS
        ↓
NORMALIZED RECORDS
        ↓
PROVENANCE + FRESHNESS
        ↓
CURRENT REALITY PROJECTION
        ↓
CHAT / OPERATOR REGISTRY
        ↓
RETRIEVAL + ROUTING
        ↓
MINIMUM CONTEXT PACK
        ↓
MOMENT ROUTER (`li now`)
        ↓
SELECTED OPERATOR
        ↓
PRODUCTION HANDOFF (when needed)
        ↓
CLAUDE / PRODUCTION CHAT
        ↓
VERIFIED RECEIPT
        ↓
UPDATED REALITY
```

## Chat/context ingestion

The first priority is to materialize chats outside the ChatGPT UI so software can address them reliably.

Required chat record:

```yaml
chat_id: stable-id
title: exact-title
source: chatgpt-export | manual-export | browser-adapter | file
created_at: ...
updated_at: ...
project: ...
topics: [...]
status: current | stale | archived
summary: ...
operators: [...]
artifacts: [...]
people: [...]
decisions: [...]
open_loops: [...]
receipts: [...]
source_ref: ...
```

Do not rely on title alone. Preserve raw transcript/source pointer.

## Structuralization

Use `chat_structuralization_prompt_pack.zip` to convert recurring chats into operator definitions:

```text
INPUT
→ RULES / TRANSFORMATION
→ TOOLS / INTEGRATIONS
→ OUTPUT
→ ACCEPTANCE
→ FAILURE PATHS
→ NEXT HANDOFF
```

Each operator must be callable without opening the original chat.

## Retrieval contract

Given a live task/event, Gemini must return:

```yaml
selected_chat_ids: [...]
selected_operator: ...
why_selected: ...
current_vs_stale_reasoning: ...
minimum_context:
  objective: ...
  verified_state: ...
  decisive_evidence: [...]
  prior_attempts: [...]
  constraints: [...]
  actors: [...]
  artifact_refs: [...]
  unresolved_unknown: ...
  requested_transition: ...
  claim_boundary: ...
```

The user should not manually copy old context between chats.

## Reality sources

The integration plane should progressively pull from:
- ChatGPT exports / project files;
- GitHub repo/issue/PR/workflow state;
- Google Calendar commitments;
- Gmail replies/follow-ups;
- Supabase/Postgres canonical state;
- browser automation receipts;
- jobs/market/community sources;
- local files/artifacts.

## Persistent automation

Use schedules/webhooks/events so context updates without manual prompting:

```text
new external event
→ ingest
→ normalize
→ update reality
→ recompute affected candidates
→ rebuild context pack if needed
→ update `li now`
```

Daily/session open should not require a manual recap.

## Production handoff contract

When the next action requires code/build work, Gemini emits:

```yaml
handoff_id: ...
owner: claude | production_chat
repo: ...
branch: ...
objective: ...
current_verified_state: ...
required_change: ...
inputs: [...]
constraints: [...]
acceptance_tests: [...]
negative_tests: [...]
claim_boundary: ...
receipt_required: ...
return_to_operator: ...
```

Claude then implements only that contract.

## Hard boundaries

- Gemini integration work must prefer existing APIs/connectors/repos/tools over new infrastructure.
- Claude production work must not reopen market/context strategy unless evidence invalidates the contract.
- Context compilation must be automatic and minimal.
- Chat navigation must become an implementation detail, not a user task.
- If a source cannot be connected live, create a fixture/import adapter and continue.
- Every normalized fact must retain provenance and freshness.
- No model-generated assertion silently becomes canonical state.

## End state

The user opens one surface and sees the correct next action with all required context already attached. Gemini keeps the integration/context plane current; Claude/production chats execute selected technical work; receipts flow back into the shared reality store automatically.
