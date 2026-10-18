# Logistinfra Composition Decision — 2026-09-19

## Decision

Do not build a bespoke user-facing Navigator shell.

Compose Logistinfra from existing mature systems and keep only the Reality/Context/Market-specific kernel custom.

## Runtime composition

1. **LibreChat = user-facing shell**
   - multi-provider/model chat
   - agents
   - MCP
   - code interpreter
   - artifacts/generative UI
   - multimodal/file handling
   - background tool calls
   - persistent user memory for convenience only
   - import ChatGPT and Claude conversation exports

2. **Logistinfra MCP server = thin custom control plane**
   Expose only:
   - sync
   - now
   - route
   - context
   - settle
   - search_workstreams
   - search_chats
   - record_feedback
   - prepare_handoff

   It wraps the already-implemented Reality Ontology / continuity / Moment Router / Market Router contracts. It is NOT a general agent framework.

3. **Composio = primary integration/auth fabric, connected directly to LibreChat**
   - managed auth
   - runtime tool discovery
   - MCP/session surface
   - event triggers where available
   - Gmail/Slack/GitHub/CRM/etc.
   The Navigator Agent gets TWO independent MCP surfaces: `Logistinfra MCP` for reality/routing/state and `Composio MCP` for external tools. Do not proxy Composio's app catalog through Logistinfra.
   Use Pipedream MCP only when a required integration is missing or materially better there.

4. **Supabase/Postgres = canonical truth/state**
   Existing Reality Ontology / workstream / transition / receipt state remains authoritative.
   LibreChat memory is never canonical truth.

5. **Existing schedulers + event sources first**
   - Composio triggers/webhooks
   - GitHub Actions for existing scheduled scans
   - LibreChat background tools for user-initiated long-running calls
   Do not add Trigger.dev until durable orchestration requirements exceed these.

6. **Langfuse = evaluation/learning plane AFTER first closed loop**
   Use traces, online evaluators, datasets, experiments and user feedback to:
   - score route quality
   - detect wrong-priority patterns
   - turn failures/corrections into regression cases
   - compare routing/prompt/model revisions
   Never let an evaluator silently rewrite Reality Ontology or authority rules.

## History materialization

### ChatGPT
Bulk export -> LibreChat native import.
Also feed the same export into the existing chat structuralizer for canonical operator/workstream extraction.

### Claude web/app
Export -> LibreChat native import.
Also structuralize for canonical state.

### Gemini Apps
Google Takeout: My Activity -> Gemini Apps.
Thin converter only if needed for LibreChat display; canonical structuralizer can ingest the export directly.

### Gemini CLI
Read project session material from the documented local session store or explicit share/export output.
Prefer supported session/share interfaces over scraping UI.

### Claude Code
Use /export, non-interactive JSON/stream-json, resume-by-session-id, hooks/status transcript_path, or Agent SDK.
Do not parse internal JSONL format as a foundational contract.

## Routing experience

User interacts with one LibreChat Agent: **Logistinfra Navigator**.

Every turn starts effectively with:
1. call logistinfra.now/sync
2. inspect canonical current state
3. decide whether the user request changes the active transition
4. dynamically discover only required tools
5. either answer directly, execute an authorized action, or generate an exact handoff

Expected UI output:
- NOW
- WHY NOW
- CURRENT STATE
- NEXT STATE
- EXACT ACTION
- TOOL / OPERATOR
- CONTEXT
- DONE WHEN
- RECEIPT
- INTERRUPT IF

Artifacts/code may render directly in LibreChat.

## Proactive path

External event
-> Composio trigger/webhook
-> tiny signed event bridge
-> Logistinfra SYNC
-> affected workstream recompute
-> priority delta test
-> if materially changed: LibreChat Agent Event (idempotent) and/or Slack notification
-> Navigator opens/continues with context already compiled

No notification when priority did not materially change.

## Compounding / anti-compounding rule

Every repeated failure, wrong-priority correction, lost follow-up, routing miss or successful pattern creates one of:
- deterministic policy update candidate
- eval dataset item
- regression test
- operator upgrade candidate
- kill/deprecation signal

No automatic policy mutation from one LLM judgment.

Promote a behavior only after repeated receipt-backed evidence.

Kill:
- duplicate agent frameworks
- duplicate memory systems
- duplicate schedulers
- custom connector layers when Composio/Pipedream/direct APIs already work
- vector DB until Postgres/search demonstrably fails
- knowledge graph until relational/event model demonstrably fails
- bespoke UI
- browser scraping when export/API/session interfaces exist

## First closed loop

Import/materialize 3 real historical chats from one Market Router workstream
-> structuralize into chat/operator/workstream records
-> start LibreChat Navigator
-> call Logistinfra MCP `now`
-> return exact next operator/context/action
-> use Composio/direct connector to perform ONE approved external action
-> independently observe receipt
-> SETTLE
-> new LibreChat conversation
-> `now` returns next transition, not previous work

That is the first production acceptance gate.
