# Gemini Ecosystem Compression Audit — Final Reuse-First Composition

You are performing the LAST pre-build ecosystem audit for Logistinfra.

Your job is not to design architecture, brainstorm agent systems, or produce a catalog.

Your job is to search the current ecosystem exhaustively enough to MINIMIZE what we build.

## Primary objective

Find the highest-leverage composition of EXISTING:

- open-source repositories
- MCP servers
- agent shells
- model routers
- session/history tools
- import/export utilities
- connector/auth fabrics
- event/trigger systems
- schedulers
- observability/eval systems
- code execution sandboxes
- UI/UX shells
- notification surfaces
- browser/computer-use systems
- memory/context systems
- research tools
- deployment templates
- community-built bridges
- starter kits
- scripts/examples

that lets us assemble a working Logistinfra Navigator with the least custom code and the shortest time to a real receipt.

Assume current date: 2026-09-19.

VERIFY current behavior against official docs and canonical repositories. Do not rely on stale blog posts or memory.

## Read these repo files FIRST

Repository:
`leadingproblemsolver/reality-ontology-runtime`

Branch:
`feat/logistinfra-runtime-v1`

Required:
- `logistinfra-runtime/COMPOSITION_DECISION_2026-09-19.md`
- `logistinfra-runtime/GEMINI_INTEGRATION_ACTUALIZER.md`
- `logistinfra-runtime/GEMINI_MINIMUM_RUNTIME_RESEARCH_PROMPT.md`
- `logistinfra-runtime/CURRENT_CONNECTOR_SURFACE.md`
- `logistinfra-runtime/TRI_PLANE_ROLE_SPLIT.md`
- `logistinfra-runtime/INTEGRATION_PLANE.md`
- `logistinfra-runtime/MOMENT_ROUTER.md`
- `logistinfra-runtime/MARKET_ROUTER_PROFIT_LOCK_PROMPT.md`
- `logistinfra-runtime/CLAUDE_COMPOSE_LOGISTINFRA_30MIN.md`
- current continuity/runtime code and tests

Also consume:
- `chat_structuralization_prompt_pack.zip`
- any available chat exports / prompt packs / existing artifacts

Do not create competing architecture if these already define authority.

## Locked authorities

- Reality Ontology = canonical evidence/current-state truth
- LCE/continuity = provenance/history
- Moment Router = immediate admissible transition
- Market Router = market-facing profitability/external-proof priority
- Gemini = integration/context discovery plane
- GPT = decision/MVExec plane
- Claude Code = production assembly/hardening plane

Preserve these unless you find concrete evidence that an existing implementation makes one unnecessary WITHOUT weakening acceptance criteria.

---

# Governing metric

Optimize every decision for:

`LEVERAGE_SCORE = (time_to_first_closed_loop_reduction × reusable_surface × external_consequence × reliability × future_compounding) / (setup_minutes + custom_code + operational_burden + lock_in + failure_surface)`

Use 1–10 normalized judgments where exact quantitative data is unavailable.

Also report:

- MINUTES_TO_BOOT
- MINUTES_TO_FIRST_ROUTE
- MINUTES_TO_FIRST_EXTERNAL_ACTION
- MINUTES_TO_FIRST_VERIFIED_RECEIPT
- NEW_LINES_OF_CUSTOM_CODE_ESTIMATE
- NUMBER_OF_NEW_SERVICES
- NUMBER_OF_MANUAL_AUTH_STEPS
- WEEKLY_MAINTENANCE_BURDEN
- PORTABILITY_RISK

A candidate that is powerful but materially slows first closure should lose unless it removes a larger downstream bottleneck.

---

# Reuse order — mandatory

For every capability test in this exact order:

1. USE_EXISTING_CONNECTED_TOOL
2. USE_EXISTING_REPO_COMPONENT
3. USE_EXISTING_EXTERNAL_PRODUCT / MCP / OSS
4. COMPOSE EXISTING COMPONENTS
5. BUILD THIN ADAPTER
6. BUILD CUSTOM COMPONENT

Never jump directly to 5 or 6.

For every final component classify it as exactly:

- REUSE_AS_IS
- CONFIGURE_ONLY
- COMPOSE
- THIN_ADAPTER
- DEFER
- KILL

---

# Research breadth

Search beyond official vendor pages.

Use:
- GitHub
- MCP registries/directories
- awesome-* lists
- GitHub Topics
- Hugging Face Spaces/repos where relevant
- Reddit technical communities
- Hacker News
- developer Discord/forum references if indexed
- product docs
- templates/starter repos
- examples from maintainers
- recent community forks
- issue/PR discussions revealing practical limitations

Community evidence should inform setup friction and failure modes, but official docs/canonical repos control capability claims.

Prefer repositories with:
- recent commits/releases
- meaningful users/stars/forks only as secondary signals
- active issues/PRs
- clear license
- Docker/self-host path
- clean APIs
- composability
- low migration cost

---

# CORE AREAS TO CLOSE

For EACH area:
1. inspect what we already have;
2. find existing solutions;
3. compare top candidates;
4. select ONE default winner;
5. name one fallback only if materially necessary;
6. identify exact integration seam;
7. state what custom work remains;
8. give acceptance test.

## A. User-facing Navigator shell

Need:
- multi-model chat
- tool/MCP calls
- multimodal input
- file upload/context
- code rendering/execution
- artifacts/generative UI
- persistent conversations
- background calls/tasks
- event-driven/proactive entry
- mobile/desktop-friendly interaction
- no bespoke frontend if avoidable

Explicitly validate current LibreChat fit.
Also search for anything materially better NOW.

## B. Model/provider routing

Need:
- OpenAI / Anthropic / Gemini and other providers
- task-dependent model selection
- fallback/routing
- ideally cost/latency awareness
- no proprietary lock-in if avoidable

Determine whether Navigator shell already solves enough.
Do not add a gateway unless justified.

## C. Logistinfra control surface

Need a standard portable way to expose:
- sync
- now
- route
- context
- settle
- search_chats
- search_workstreams
- record_feedback
- prepare_handoff

Evaluate MCP server frameworks/templates.
Select the thinnest production-ready implementation for the existing TypeScript/Python codebase.

## D. Historical chat/session materialization

Find the fastest reliable path for:

### ChatGPT
- full export/import
- incremental options if any
- attachments/files where possible
- project/title/timestamps preservation

### Claude web/app
same requirements

### Gemini Apps
same requirements

### Gemini CLI
session/history interfaces

### Claude Code
session/export/SDK/hooks/transcript interfaces

Search for existing converters/importers/aggregators that reduce custom normalization.

Do not use undocumented scraping unless every supported path fails.

Distinguish:
- BULK_BOOTSTRAP
- INCREMENTAL_SYNC
- LIVE_EVENT_STREAM

We need bulk bootstrap immediately.
Incremental sync may be thinner than a true live stream.

## E. Chat structuralization / context extraction

We already have a structuralization prompt contract.

Search for:
- existing schema extraction frameworks
- conversation parsers
- LLM structured-output libraries
- incremental summarization/change detection
- provenance-aware extraction
- event sourcing patterns

Use existing libraries where they eliminate code.
Do not replace our operator schema with a generic memory abstraction.

## F. Canonical state / Reality Ontology

We already have Supabase/Postgres direction and schema.

Test whether anything needs replacing.
Default answer should be NO unless concrete evidence shows a major leverage win.

Find useful Postgres-native capabilities we can exploit before adding systems:
- JSONB
- full-text search
- pg_trgm
- vector only if actually needed
- pg_cron
- realtime
- Edge Functions
- queues/extensions if relevant

## G. Search / retrieval

Determine the minimum adequate path for:
- exact title
- alias
- project
- artifact
- actor
- decision
- open loop
- semantic/task relevance

Test whether Postgres FTS/trigram + bounded LLM rerank is enough.

Do not add a vector DB unless you can demonstrate a specific retrieval class that fails.

## H. Connector/auth/action fabric

Validate current Composio decision against:
- Pipedream MCP
- direct MCP servers
- provider-native APIs
- other current integration fabrics

Score:
- app coverage
- OAuth/auth
- runtime tool discovery
- triggers
- reliability
- pricing
- MCP quality
- rate limits
- self-host/escape path
- logging
- approvals
- verification friendliness

We prefer TWO MCP surfaces:
- Logistinfra MCP for truth/routing
- external integration MCP for real-world actions

Do not proxy thousands of actions through custom code.

## I. Proactive/event-driven execution

Need:
external event
→ normalized observation
→ SYNC
→ affected workstream recompute
→ priority delta
→ notify/continue ONLY if materially changed

Research:
- Composio triggers
- shell-native agent events
- webhooks
- Supabase Realtime/Edge Functions
- GitHub webhooks/Actions
- Slack notifications
- anything already built that eliminates our event bridge

Find the absolute thinnest composition.

## J. Human approval / authority

Need:
- consequential writes gated
- optional remembered scopes
- action previews
- explicit approvals
- irreversible actions stricter
- read-only background operations freer

Use shell/MCP/tool-native approval mechanisms where possible.
Identify exactly what remains ours.

## K. Independent verification / receipts

Need:
tool success ≠ state success.

For common actions:
- email sent
- GitHub mutation
- deployment
- form submission
- payment
- CRM update
- browser action

find the simplest fresh-observation verification patterns using existing connectors/APIs.

Determine whether any framework already supports expected-action verification that we can reuse.

## L. Browser/computer use

Only for surfaces without stable APIs/MCP.

Compare:
- Browser Use
- Playwright
- other current agent-browser/computer-use systems

Need:
- reusable authenticated sessions
- structured observations
- deterministic selectors where possible
- screenshots/traces
- fresh verification
- recovery
- minimal setup

Select one primary and one fallback at most.

## M. Claude Code / implementation handoff

Find the fastest way for Navigator to:
- create bounded production handoff
- invoke or route to Claude Code
- preserve session ID
- receive structured output
- inspect tests/receipts
- resume later

Prefer existing Claude Code CLI/SDK/MCP/hooks integrations.

Do not wrap Claude Code unnecessarily.

## N. Deployment

Find fastest stable deployment path for:
- LibreChat/shell
- Logistinfra MCP
- event webhook
- Supabase connection

Prefer:
- existing Docker compose
- Railway/Render/Fly/Vercel/Netlify where appropriate
- existing deployment templates

Score setup minutes and operational burden.

## O. Evaluation / self-improvement / compounding

Need:
- traces
- route-quality scoring
- WRONG_PRIORITY feedback
- operator success rates
- external consequence metrics
- failures → regression dataset
- candidate prompt/policy changes
- experiments against historical failures
- promote only after receipt-backed improvement

Validate Langfuse and search current alternatives.

Do NOT build self-modifying policy.

Required loop:
behavior
→ trace
→ external/user outcome
→ eval
→ dataset/regression case
→ candidate revision
→ replay/experiment
→ human/policy gate
→ promote or kill

## P. Predictive / anti-negative-compounding layer

Search for reusable pieces that help detect:
- missed commitments
- lost follow-ups
- waiting-state expiry
- repeated failure classes
- stale projects
- growing WIP
- foundation/skill decay
- repeated AI dependence on same primitive
- lack of external actions
- financial/admin deadlines
- system failures

Do not create a second productivity app.

Determine which signals can come directly from existing state/connectors and what scoring logic truly needs custom code.

## Q. Market Router / profitability path

Market Router remains non-negotiable.

Test whether the composition supports:

existing proof/artifact
→ live signal
→ exact actor
→ intervention
→ approved execution
→ external receipt
→ proof
→ next target

Every infrastructure choice should be evaluated against this path.

## R. Security / secrets / privacy

Need minimum safe deployment:
- secrets outside prompts/state
- least-privilege auth
- local handling where appropriate
- audit logs
- reversible actions
- source provenance
- user-owned data export
- vendor escape path

Reuse platform security capabilities rather than inventing systems.

---

# REQUIRED GAP ANALYSIS

After researching all areas, produce exactly three gap classes:

## GAP 0 — NOTHING TO BUILD
Existing component solves it sufficiently.

## GAP 1 — CONFIG/COMPOSITION ONLY
Requires config, auth, schema mapping, prompt, deployment, or glue but no meaningful product code.

## GAP 2 — TRUE THIN CODE GAP
No existing component adequately satisfies the contract.

For every GAP 2 item specify:
- why existing systems fail;
- smallest interface;
- estimated LOC;
- estimated build minutes with Claude Code;
- exact acceptance test;
- whether it blocks the FIRST CLOSED LOOP.

If a GAP 2 does not block first closure, DEFER it.

---

# REDUNDANCY / KILL AUDIT

Explicitly search our repo and proposed stack for overlapping responsibility.

Kill or defer any duplicate:
- router
- memory system
- agent framework
- scheduler
- event bus
- integration proxy
- DB
- vector store
- knowledge graph
- browser engine
- eval system
- UI
- notification layer
- workflow builder
- prompt that has already been superseded

Return exact repo files/components that can be archived or treated as reference-only if they are now redundant.

Do NOT delete anything yourself.

---

# USER EXPERIENCE TEST

The final composition must support this without the user manually navigating infrastructure:

User opens Navigator and says:
> what now?

System:
1. synchronizes relevant live state;
2. returns ONE primary action;
3. explains why in one line;
4. points to exact chat/operator/tool/artifact;
5. has the minimum context already loaded;
6. can answer directly OR call the correct model/tool;
7. can render code/artifacts/UI when appropriate;
8. can request approval for consequential action;
9. independently verifies outcome;
10. SETTLEs;
11. proactively resurfaces only when reality materially changes.

Also support:
> continue X

without making the user reconstruct X.

And:
> this priority is wrong

which becomes an eval/regression signal, not an uncontrolled policy mutation.

---

# 30-MINUTE ASSEMBLY CONSTRAINT

Optimize explicitly for a first useful composition that a capable Claude Code agent can assemble in approximately one focused session.

Do not claim false precision on elapsed time.

Instead separate:

### CAN CONFIGURE IMMEDIATELY
no meaningful coding

### CLAUDE CAN ASSEMBLE DIRECTLY
bounded code/config from verified docs/templates

### REQUIRES HUMAN AUTH
OAuth, secrets, account creation, exports

### CANNOT CLOSE YET
real blocker

The goal is to minimize the last two.

---

# SEARCH STOP RULE

Do not search forever.

For each area, stop when:
- one candidate satisfies all blocking acceptance criteria;
- alternatives do not offer a material (>20%) leverage improvement;
- portability/maintenance risk is acceptable;
- first-closure path is clear.

Spend research depth on uncertain/blocking areas, especially:
1. cross-platform history materialization;
2. user-facing agent shell/event behavior;
3. connector/auth fabric;
4. verification/receipts;
5. Claude Code invocation/handoff;
6. eval/compounding.

---

# OUTPUT — NO ESSAY

## 1. FINAL COMPOSITION

One table only:

AREA | WINNER | CLASSIFICATION | EXACT ROLE | WHY | SETUP MIN | CUSTOM LOC | BLOCKS FIRST LOOP? | SOURCE

## 2. FIRST-CLOSED-LOOP GRAPH

Show the exact selected systems in:

history
→ structuralize
→ canonical state
→ Navigator
→ route
→ action
→ verify
→ settle
→ proactive next route

## 3. IRREDUCIBLE GAP LIST

Only GAP 2 items.

Order by:
`first-loop impact / Claude build effort`.

## 4. CONFIG/AUTH CHECKLIST

Exact actions the human must do.

No generic instructions.

## 5. CLAUDE CODE PACKET

Produce ONE copy-paste production handoff containing:
- repositories/templates to clone/use;
- exact packages;
- exact files to modify/create;
- configs;
- env var names;
- commands;
- acceptance tests;
- negative tests;
- stop condition.

Claude must be told to reuse/copy upstream code/config where licensed rather than reimplement.

## 6. MODEL/TASK ROUTING MAP

For each common Logistinfra task select the best available execution surface:
- direct deterministic code
- GPT
- Gemini
- Claude/Claude Code
- browser/computer use
- connector/MCP
- human

Do not route LLMs where code or direct APIs are more reliable.

## 7. PROACTIVE EVENT MAP

EVENT | SOURCE | TRIGGER | STATE CHANGE | PREEMPT? | DELIVERY SURFACE

## 8. EVAL / COMPOUNDING MAP

SIGNAL | EVAL | DATASET/REGRESSION ACTION | PROMOTE/KILL RULE

## 9. KILL LIST

Everything we should NOT build or activate yet.

## 10. FINAL VERDICT

End with exactly:

REUSE_AS_IS:
CONFIGURE_ONLY:
COMPOSE:
THIN_CODE_GAPS:
HUMAN_AUTH_REQUIRED:
FIRST_CLOSED_LOOP:
FIRST_REAL_RECEIPT:
ESTIMATED_CUSTOM_LOC:
NEW_SERVICES_REQUIRED:
BIGGEST_UNRESOLVED_RISK:
EXACT_NEXT_CLAUDE_HANDOFF:
STOP_RESEARCH_AND_BUILD_NOW: YES/NO

If NO, identify exactly one blocking research question. No broad caveats.
