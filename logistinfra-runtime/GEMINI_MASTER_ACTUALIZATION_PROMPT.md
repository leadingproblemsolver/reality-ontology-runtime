# Gemini Master Actualization Prompt — Logistinfra

You are operating inside the repository `leadingproblemsolver/reality-ontology-runtime` on branch `feat/logistinfra-runtime-v1`.

Your job is **not** to design another architecture document. Your job is to **turn Logistinfra into an executable system**, starting with the missing front door: the ability to ingest, retrieve, navigate, structuralize, and execute from our accumulated chats and files without requiring the human to remember which conversation, project, prompt, or artifact to open.

## Core objective

Build a persistent runtime that can repeatedly do this from a fresh process:

```text
CURRENT MOMENT
+ active goals
+ commitments/deadlines
+ external replies/events
+ current project states
+ chat-derived decisions/operators
+ evidence
+ waiting/blocked states
+ available time
        ↓
RECONSTRUCT REALITY
        ↓
FIND THE RELEVANT PRIOR CHAT / DECISION / OPERATOR
        ↓
COMPILE ONLY THE MINIMUM CONTEXT
        ↓
SELECT THE SINGLE HIGHEST-VALUE DEPENDENCY-CORRECT NEXT ACTION
        ↓
ROUTE TO THE CORRECT OPERATOR
        ↓
EXECUTE / PREPARE / ASK FOR APPROVAL
        ↓
VERIFY WHAT ACTUALLY HAPPENED
        ↓
PERSIST EVIDENCE + NEW STATE
        ↓
SETTLE + CHOOSE NEXT TRANSITION
```

The user should progressively stop needing to remember:

- which chat owns what;
- what was previously decided;
- what context to paste;
- which project is most urgent;
- what is waiting;
- which tool/site to open;
- whether the correct next move is research, build, contact, verify, follow up, settle, or stop.

The system must answer:

> **Given what is true right now, what is the single highest-value dependency-correct action, which operator owns it, what minimum context is required, and what receipt ends the block?**

---

# SOURCE MATERIAL — READ BEFORE CODING

Inspect and preserve the intent of the existing runtime files before changing anything:

```text
logistinfra-runtime/README.md
logistinfra-runtime/INTEGRATIONS.md
logistinfra-runtime/CLAUDE_CODE_PROMPT.md
logistinfra-runtime/MOMENT_ROUTER.md
logistinfra-runtime/MOMENT_ROUTER_CLAUDE_PROMPT.md
logistinfra-runtime/moment_router.py
logistinfra-runtime/reality.example.json
logistinfra-runtime/test_moment_router.py
logistinfra-runtime/RUN_20_MIN.md
```

Also inspect any attached/materialized chat structuralization pack, chat exports, conversation archives, markdown/docx/pdf extracts, prompt packs, and project files available in the working environment.

The chat structuralization source is intended to convert chats into durable operators with this shape:

```text
INPUT
→ transformation/rules
→ tools
→ OUTPUT
→ acceptance gate
→ failure paths
→ next handoff
```

Do not throw away nuance from the original chat. Preserve provenance back to the exact source conversation/file/chunk whenever possible.

Human ownership gates remain separate from machine-generated evidence. Human-owned work should be able to accumulate into durable acceptance/invariant/failure/authority/reconstruction/verification/claim-boundary/settlement files rather than disappearing into chat.

---

# NON-NEGOTIABLE IMPLEMENTATION ORDER

You must build the system in this order. Do not jump ahead because later layers depend on earlier ones.

## PHASE 0 — RECONNAISSANCE / NO REDESIGN

1. Inspect the repository and current runtime.
2. Enumerate what already exists and what is missing.
3. Reuse current code/contracts rather than replacing them.
4. Produce `logistinfra-runtime/ACTUALIZATION_STATUS.md` containing:
   - existing working components;
   - partial components;
   - missing components;
   - dependencies;
   - exact execution order.

Do not spend more than a small fraction of the task on this document.

---

# PHASE 1 — MAKE THE CHAT CORPUS ADDRESSABLE

This is the first hard gate.

The runtime cannot route to chats if chats are not addressable from software.

Implement a chat corpus subsystem under something like:

```text
logistinfra-runtime/chat_runtime/
├── ingest.py
├── normalize.py
├── models.py
├── index.py
├── retrieve.py
├── structuralize.py
├── registry.py
├── context_compile.py
└── cli.py
```

Exact names may vary only if the repository conventions demand it.

### Required supported input forms

Support at least:

- ChatGPT export JSON/HTML if present;
- markdown/text conversation files;
- prompt-pack files;
- individual extracted conversation files;
- manually provided chat metadata;
- future adapters for API/browser-based retrieval.

Do not block the MVP on direct ChatGPT UI automation.

### Canonical chat record

Every conversation must become an addressable record with fields equivalent to:

```yaml
chat_id:
title:
persona:
created_at:
updated_at:
source_type:
source_ref:
participants:
projects: []
goals: []
entities: []
artifacts: []
decisions: []
commitments: []
open_loops: []
operators: []
claims: []
receipts: []
summary:
raw_content_ref:
```

Preserve raw source separately. Derived fields are not canonical truth.

### Acceptance

From a fresh process, point the ingester at a fixture/sample corpus and prove:

1. multiple chats are discovered;
2. each receives a stable ID;
3. raw provenance is retained;
4. duplicate ingestion is idempotent;
5. chats can be retrieved by title, project, goal, actor, artifact, and semantic/task relevance;
6. the retrieved result points back to its exact source.

Negative tests:

- duplicate file;
- malformed export;
- missing title;
- mixed persona corpus;
- irrelevant chat outranks exact relevant chat;
- stale copied chat should not silently override a newer canonical state.

Stop Phase 1 only when this works.

---

# PHASE 2 — CHAT → OPERATOR STRUCTURALIZATION

Turn recurring high-value chats into reusable operator definitions.

Do NOT summarize every chat into generic prose.

Extract operational contracts.

Create a schema equivalent to:

```yaml
operator_id:
name:
source_chat_ids: []
purpose:
invoke_when: []
accepts: []
preconditions: []
rules: []
tools: []
returns: []
acceptance: []
failure_paths: []
next_handoffs: []
authority_level:
claim_boundary:
version:
provenance: []
```

Start with the existing high-value operating chats/workstreams:

1. Operational Research Strategy
2. High-Value Inelastic Problems
3. Signal / ICP Pain Extraction
4. Constraint Intelligence
5. Shipping Strategy Framework
6. Platform Stack Strategy
7. Market Router
8. Artifact Campaign Creation
9. Message Triage Process
10. Direct GTM / Recruitment Conversion
11. Next Steps Execution Plan
12. Evidence-to-Impact
13. Proof Deployment / Outcome Mapping
14. Internship / employer conversion
15. End-of-day settlement
16. relevant build/spec/verification operators already represented in the repo

If literal chat titles differ, use the recovered source titles and preserve aliases.

### Structuralization rule

Every operator must explicitly preserve:

```text
INPUT
RULES
TOOLS
OUTPUT
ACCEPTANCE
FAILURE
HANDOFF
```

No operator is considered real if it only contains a prompt and no acceptance/failure contract.

### Acceptance

Given a task like:

> “We have a qualified live target and evidence, but no intervention selected.”

The registry must deterministically retrieve `Market Router` or its equivalent operator and return the required input contract.

Given:

> “A real external reply arrived.”

The registry must retrieve `Message Triage Process` or equivalent before generic outreach generation.

---

# PHASE 3 — CHAT NAVIGATION / RETRIEVAL ENGINE

Implement a user-facing navigation layer that can answer:

```text
Which prior chat/workstream contains the relevant decision?
Which exact operator should own this task?
What prior artifact/URL/receipt does it depend on?
What did we already try?
What remains unresolved?
```

Create commands equivalent to:

```bash
li chat find "market router"
li chat find --task "reply from founder after audit"
li chat show <chat_id>
li operator find --task "choose channel for live target"
li context <operator_id> --task "..."
```

Do not return ten chats if one dominates.

Retrieval ranking must combine inspectable signals such as:

- literal title/alias match;
- project overlap;
- goal overlap;
- entity overlap;
- artifact overlap;
- decision/open-loop relevance;
- freshness where relevant;
- semantic similarity;
- operator invoke conditions.

LLM reranking may be used only after deterministic retrieval has produced a bounded candidate set.

### Acceptance

Test at least five representative user intents and prove that the right chat/operator is surfaced ahead of adjacent-but-wrong workstreams.

---

# PHASE 4 — MINIMUM CONTEXT COMPILER

Implement a context compiler that prevents full-chat dumping.

For the selected operator/action, compile only:

```yaml
objective:
current_verified_state:
relevant_recent_history:
decisions:
constraints:
evidence:
actors:
artifacts:
open_loops:
previous_attempts:
unknowns:
authority_boundary:
claim_boundary:
requested_transition:
source_refs: []
```

Every compiled context pack must have a stable ID and be persisted so a fresh process can resume the same action.

Commands equivalent to:

```bash
li context compile --operator market_router --task "..."
li context show <context_pack_id>
```

### Acceptance

From a fresh process:

1. compile a context pack;
2. terminate process;
3. reopen;
4. retrieve by ID;
5. prove it contains the decisive information but not the entire source corpus.

---

# PHASE 5 — MOMENT ROUTER INTEGRATION

Do not rewrite the existing Moment Router from scratch.

Upgrade it so candidate actions can reference:

- chat IDs;
- operator IDs;
- context pack IDs;
- actual source evidence;
- waiting state;
- current execution state;
- deadlines/commitments when available.

`li now` must return at most:

```yaml
primary:
  action:
  why_now:
  operator_id:
  chat_refs: []
  context_pack_id:
  first_physical_action:
  stop_condition:
  receipt_required:
  timebox_minutes:

interruption_lane:
  condition:
  operator_id:
  action:
```

No dashboard wall.

No project menu.

No “choose one of these 12 chats.”

### Hard priority rules

Before scoring normal candidates, deterministically preempt for:

1. safety/security;
2. external actor waiting with meaningful consequence;
3. deadline entering action window;
4. live production/user blocker;
5. already-approved time-sensitive consequential action.

Waiting-on-external work must be suppressed until its trigger changes.

---

# PHASE 6 — REALITY STORE / STATE MODEL

Unify chat-derived state and execution-derived state without pretending they are equivalent.

Minimum objects:

```text
Actor
Goal
Object/Project
State
Event
Evidence
Decision
Commitment
OpenLoop
Operator
Execution
Approval
ContextPack
ChatSource
Artifact
```

Canonical truth principles:

- raw external/source evidence is preserved;
- derived summaries are projections;
- LLM output never becomes canonical fact merely because it was generated;
- state transitions require evidence;
- contradictions remain visible;
- UNKNOWN is a valid state.

Persist state using the existing intended Postgres/Supabase boundary when practical. Do not block early tests on remote infrastructure; local deterministic fixtures are acceptable first.

---

# PHASE 7 — EXECUTION RUNTIME

Convert selected operator output into durable executions.

Execution state machine must support at least:

```text
PREPARED
AWAITING_APPROVAL
RUNNING
WAITING
RETRYING
SUCCEEDED
FAILED
INCONCLUSIVE
CANCELLED
```

Every consequential operator follows:

```text
prepare
→ check preconditions
→ check authority
→ execute
→ observe fresh state
→ verify
→ persist evidence
→ transition state
```

A tool returning “success” must never be treated as proof that reality changed.

---

# PHASE 8 — ADAPTERS / REAL-WORLD INTERACTION

Use narrow adapters, not a universal agent abstraction.

Progressively add:

1. GitHub API
2. Calendar
3. Gmail/email
4. HTTP/browser
5. Browser Use / Playwright
6. market/job sources
7. CRM/Apollo where available

Each adapter must implement a bounded contract:

```text
prepare
execute
observe
verify
```

Browser execution must verify expected page/state transitions through a fresh observation rather than trusting the action call.

External writes require explicit authority policy.

---

# PHASE 9 — BACKGROUND / PERSISTENT TRIGGERS

Start with GitHub Actions / simple scheduler already present.

Add richer durable scheduling only when needed.

Triggers should include:

- session/open;
- primary completion/failure;
- inbound external event;
- deadline/calendar boundary;
- blocker clear;
- hourly source scan where freshness matters;
- morning/daypart compilation.

The system should be capable of precomputing the likely first action before the user manually navigates anything.

---

# PHASE 10 — HUMAN CORRECTION / LEARNING

Support explicit user feedback actions:

```text
START
DONE
BLOCKED
WAITING
WRONG_PRIORITY
SNOOZE
REJECT
```

Corrections become evidence.

Do not silently mutate hard priority policy based on one correction.

Repeated successful procedures may later graduate from:

```text
novel human+agent procedure
→ reusable operator
→ workflow
→ deterministic automation
```

but only after evidence of repetition.

---

# PHASE 11 — PROOF / CLAIM BOUNDARY

Every completed execution must be capable of producing:

```yaml
action_taken:
external_receipt:
what_became_true:
what_did_not_become_true:
capability_demonstrated:
market_or_technical_learning:
relationship_or_access_change:
claim_boundary:
source_refs: []
next_transition:
```

Never rewrite:

- no reply → validated demand;
- deployment → production usage;
- generated code → independently owned engineering;
- attempted action → successful state transition;
- historical test → current verified state.

---

# PHASE 12 — USER EXPERIENCE

The user experience should collapse toward one entry point:

```bash
li now
```

Example desired output:

```text
NOW

PRIMARY
Reproduce Browser Use reliability bug

WHY NOW
Live contribution opportunity; strongest proof gap; 45 minutes free; no external actor currently waiting.

USE
operator: github_contribution
context: ctx_0192
sources: chat_0041, issue_5438

FIRST ACTION
Run missing-element reproduction test.

DONE WHEN
Failing test + trace persisted.

INTERRUPT ONLY IF
Maintainer reply / urgent external response / deadline preemption.
```

The user must not need to decide which chat to open first.

---

# FIRST END-TO-END ACCEPTANCE TEST

Do not claim success until this scenario passes from a fresh process:

### Fixture state

There are at least:

- three competing active tasks;
- one task waiting on an external actor;
- one relevant prior chat defining an operator;
- one old adjacent chat that should not be selected;
- one active proof gap;
- one bounded current time window.

### Required behavior

1. ingest/retrieve the relevant chat corpus;
2. find the correct operator;
3. suppress waiting work;
4. rank the active candidates;
5. return exactly one primary move;
6. compile a persisted minimum context pack;
7. show exact source provenance;
8. provide first physical action;
9. define stop condition + receipt;
10. persist an execution record;
11. after completion/failure, rerun and choose the next state correctly.

### Hostile variants

- urgent external reply arrives → must preempt ordinary work;
- top chat retrieval result is stale copy → must expose freshness/provenance instead of silently trusting it;
- operator input is incomplete → must expose missing evidence, not hallucinate;
- previous execution failed after possible side effect → verify before retry;
- no candidate fits available time → choose a smaller dependency-correct action or return explicit NO_SAFE_ACTION;
- duplicate ingestion/run → no duplicate canonical event/action.

---

# IMPLEMENTATION DISCIPLINE

## You MAY

- create/modify code;
- create tests/fixtures/migrations;
- run local tests;
- inspect repository history;
- use deterministic parsers/indexes;
- use SQLite locally for bootstrap if needed while preserving a clean Postgres boundary;
- add CLI commands;
- add narrow adapters;
- use an LLM only where ambiguity requires it.

## You MUST NOT

- stop at an architecture document;
- replace working code because a new framework looks cleaner;
- build a dashboard before the runtime works;
- introduce a graph/vector database unless a measured retrieval failure requires it;
- create an agent swarm;
- make chat summaries canonical truth;
- automatically perform consequential external writes without an authority gate;
- fabricate completion because mocks passed;
- claim full Logistinfra when only one layer works.

---

# REQUIRED WORKING TREE TARGET

Prefer a structure approximately like:

```text
logistinfra-runtime/
├── chat_runtime/
│   ├── ingest.*
│   ├── normalize.*
│   ├── models.*
│   ├── index.*
│   ├── retrieve.*
│   ├── structuralize.*
│   ├── registry.*
│   └── context_compile.*
├── operators/
│   ├── registry/
│   └── schemas/
├── reality/
├── execution/
├── adapters/
├── evidence/
├── fixtures/
├── tests/
├── moment_router.py
├── MOMENT_ROUTER.md
└── ACTUALIZATION_STATUS.md
```

Adapt to repository conventions rather than forcing these names.

---

# OUTPUT / REPORTING RULE

Work continuously through the implementation rather than asking for confirmation at every substep.

At meaningful closure points, report only:

```text
IMPLEMENTED
VERIFIED
FAILED / STILL MISSING
EXTERNAL OR FIXTURE RECEIPT
NEXT DEPENDENCY
```

If blocked by credentials/integration access:

1. fully implement and test the adapter boundary against fixtures;
2. document the exact missing credential/action;
3. continue every other dependency that does not require it.

Do not stop the whole task because one external integration is unavailable.

---

# TERMINAL DEFINITION OF DONE

The system is not done when it can search chats.

It is done only when the following loop is executable:

```text
CHAT/FILE HISTORY
→ addressable corpus
→ operator registry
→ current reality
→ relevant retrieval
→ minimum context
→ one next action
→ durable execution
→ approval if required
→ real/fake adapter execution depending environment
→ independent verification
→ evidence
→ state update
→ settlement
→ next action
```

Start with **Phase 1 immediately**.

Do not ask me which chat to start with.

Discover the available corpus, create fixtures if needed, implement the chat ingestion/retrieval boundary, test it, and then continue in dependency order.