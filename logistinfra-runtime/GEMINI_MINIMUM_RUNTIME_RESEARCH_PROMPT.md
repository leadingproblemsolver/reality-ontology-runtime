# Gemini Prompt — Minimum Viable Systems for Automated Chat-to-Market Runtime

Use current web research as of September 2026. Verify every claimed tool/repository against official docs and/or the live GitHub repository before recommending it.

## Inputs you must consume first

1. `MARKET_RUNTIME_CONTRACT` produced by our Market Router.
2. `chat_structuralization_prompt_pack.zip`.
3. Repository: `leadingproblemsolver/reality-ontology-runtime`, especially branch `feat/logistinfra-runtime-v1`.
4. `logistinfra-runtime/MOMENT_ROUTER.md`.
5. `logistinfra-runtime/MARKET_ROUTER_PROFIT_LOCK_PROMPT.md`.
6. Any current asset/proof inventory provided alongside this prompt.

Do not ignore these inputs and invent a separate architecture.

# Objective

Find the smallest, cheapest, currently usable set of systems, open-source repositories, APIs, integrations, or code-first tools that can convert our valuable chat history into a persistent runtime that repeatedly:

chat/artifact/source
→ structuralize reusable value
→ register operator/state/asset/evidence
→ detect live market opportunity
→ select the highest-profitability next action
→ compile the minimum context
→ prepare or execute the action
→ verify the external state change
→ persist the receipt
→ route proof into the next buyer/user/employer/community action

We care about profitability and external proof, not automation for its own sake.

# Baseline architecture every recommendation must beat

Assume we can already build the following with ordinary code:

- GitHub repo as canonical code/config surface
- GitHub Actions for simple scheduled jobs
- Supabase/Postgres for canonical state
- plain Python or TypeScript structuralizer scripts
- structured LLM outputs for ambiguous extraction/scoring
- direct APIs wherever available
- Browser Use or Playwright only where APIs do not exist
- human approval before consequential external actions

Do NOT recommend an extra platform unless it materially improves setup time, reliability, durability, observability, cost, or conversion speed over that baseline.

# Systems to solve

Research minimum viable options for each of these, but merge roles whenever one simple system can safely cover multiple functions:

1. CHAT / FILE INGESTION
   - exported ChatGPT conversations, markdown, JSON, docs, zips
   - detect new/changed source material

2. CHAT-TO-OPERATOR STRUCTURALIZER
   Extract:
   - purpose
   - invoke_when
   - inputs
   - deterministic rules
   - LLM judgment
   - outputs
   - acceptance test
   - failure path
   - next operator
   - relevant artifacts
   - unresolved state
   - evidence / claim boundaries

3. OPERATOR / ASSET REGISTRY
   - versioned operators
   - prompts
   - artifacts
   - URLs/repos/files
   - source provenance

4. PERSISTENT REALITY / MARKET STATE
   Minimum entities:
   - signals
   - targets
   - opportunities
   - interventions
   - executions
   - approvals
   - waiting states
   - relationships
   - evidence/receipts
   - assets
   - proof objects

5. MOMENT ROUTER
   Given current time, deadlines, replies, blockers, waiting states, available time, live opportunities and proof gaps, return:
   - one primary move
   - one interruption lane
   - exact operator
   - minimum context pack
   - stop condition
   - receipt required

6. BACKGROUND ORCHESTRATION
   - schedules
   - event triggers
   - queues
   - retries
   - idempotency
   - durable waiting
   - human approval where needed

7. LIVE MARKET SIGNAL COLLECTION
   Relevant sources may include:
   - GitHub
   - Gmail
   - LinkedIn
   - X
   - Reddit
   - company sites
   - job boards
   - Apollo/CRM
   - communities
   Prefer direct APIs/connectors before browser automation.

8. INTERVENTION EXECUTION
   - email
   - GitHub issue/PR/comment
   - forms
   - applications
   - browser actions
   - other bounded external writes
   Human approval must remain available.

9. INDEPENDENT VERIFICATION / RECEIPTS
   Verify that expected external state actually changed.
   Tool success alone must never equal outcome success.

10. PROOF COMPILER / DISTRIBUTION
   Verified receipt
   → claim boundary
   → case fragment / README / portfolio / CV / application evidence / sales attachment / public post
   → next relevant recipient.

# Research constraints

For every candidate tool/repository/platform verify:

- exact current name and URL
- official docs or canonical repo
- open-source vs proprietary
- license
- last meaningful release/commit/activity
- self-hostable? yes/no
- hosted option? yes/no
- free/cheap path
- required infrastructure
- supported language/runtime
- cron/event support
- retries/queues/durable waits
- human approval support
- observability/logging
- API/webhook support
- Git integration
- secret handling
- browser support if relevant
- setup time for one competent engineer using Claude Code/Codex
- maintenance burden
- lock-in / escape path

Mark anything you cannot verify as `UNVERIFIED`.

# Profitability filter

For each proposed component calculate or qualitatively assess:

- time saved per week
- reduction in switching/reconstruction cost
- reduction in missed follow-ups
- increase in external attempts
- increase in substantive replies/access
- increase in verified proof events
- likelihood it shortens time-to-payment / time-to-employer-proof
- implementation time
- ongoing cost
- failure cost

If a tool does not improve the Market Router loop, exclude it.

# Required output

## A. RECOMMENDED MINIMUM STACK
No more than 5 core components if possible.

For each:
- ROLE
- TOOL / REPO
- WHY THIS ONE
- WHY NOT THE ALTERNATIVES
- COST
- SETUP TIME
- EXACT MARKET ROUTER STAGES IT ENABLES
- PROFITABILITY LEVER
- FAILURE / ESCAPE PATH

## B. BASELINE VS RECOMMENDED
Compare your stack against:
GitHub Actions + Supabase/Postgres + plain scripts + LLM structured outputs + direct APIs + Browser Use/Playwright.

Only keep additions that beat the baseline.

## C. FIRST 24-HOUR BUILD
Give an exact dependency-correct implementation sequence.
Each step must include:
- command/setup action
- file(s) created/changed
- environment variables
- acceptance test
- receipt/output
- stop condition

## D. CHAT STRUCTURALIZATION PIPELINE
Specify exact schemas and a concrete example converting one chat into:
- operator YAML/JSON
- context pack
- state update
- asset references
- next-operator edge

## E. MARKET ROUTER INTEGRATION
Show exactly how the Market Router contract enters the runtime and how:
- opportunities are ranked
- only one primary action is surfaced
- waiting states disappear until wake conditions occur
- external replies can preempt current work
- profitability/proof priority is preserved

## F. AUTOMATION ORDER
Rank all proposed automations by:
`expected external/profitability leverage ÷ implementation effort`.

Use only:
- BUILD NOW
- BUILD AFTER RECEIPT
- DO NOT BUILD

## G. EXISTING REPOS / SYSTEMS TO REUSE
Search GitHub and the web for existing projects that already solve substantial pieces of the above. Prefer active, composable, code-first repositories over visual automation SaaS.

For each give:
- repo
- exact component we can reuse
- integration seam
- what we still need to build
- license
- current maintenance signal

## H. FINAL DECISION
End with exactly:

`STACK TO IMPLEMENT NOW:`
`FIRST CLOSED LOOP:`
`FIRST EXTERNAL RECEIPT:`
`TOTAL NEW COMPONENTS:`
`ESTIMATED SETUP BURDEN:`
`DO NOT BUILD YET:`

# Critical prohibitions

Do not propose:
- a generic agent swarm
- a knowledge graph unless directly required by proven retrieval failure
- a vector database unless ordinary indexed Postgres/search demonstrably fails
- a dashboard before the CLI/notification loop works
- n8n merely because it has many integrations
- scraping where a stable API exists
- automatic consequential writes without authorization
- systems that generate more internal artifacts without advancing an external market state

The test is simple: does this system help us turn existing accumulated work into more real buyer/user/employer/community interactions, receipts, proof, and eventually revenue? If not, remove it.
