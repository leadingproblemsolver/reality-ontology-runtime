# CLAUDE EXECUTION PACKET — Finish V1, Then Operational Reality

You are operating on:
- parent: `operational-reality-v1`
- deployable runtime base: `immediatelyusable`

Your job is to FINISH, not redesign.

## NON-NEGOTIABLE AUTHORITY

- Reality Ontology owns canonical truth.
- Moment Router owns immediate transition selection.
- Market Router owns market-facing economic priority.
- Claude owns implementation/hardening only.
- Tool success != outcome success.
- Every consequential effect requires fresh external verification before settlement.
- Existing tools/integrations/repos first. Thin glue only when an acceptance test proves it necessary.
- No new ontology, router, scheduler, memory system, task manager, agent framework, UI, OAuth framework, scraper fleet, CRM wrapper, or queue.

---

# PHASE 0 — RECONSTRUCT CURRENT REALITY

Before changing code:

1. inspect current branch heads:
   - `immediatelyusable`
   - `operational-reality-v1`
   - all `or/*` children
2. inspect latest CI/workflows;
3. inspect current implementation vs prompt-only files;
4. identify exact missing seams;
5. preserve all already-settled architecture decisions;
6. do not reopen design.

Return internally:

```yaml
verified_current_state:
missing_runtime_seams:
missing_operational_reality_seams:
branch_hygiene_issues:
first_dependency_correct_step:
```

Then execute.

---

# PHASE 1 — COMPLETE `immediatelyusable`

Run the existing series in dependency order:

1. `01_SUPABASE_STORE.md`
2. `02_MCP_HTTP_FACADE.md`
3. `03_LIVE_READ_BINDINGS.md`
4. `04_GITHUB_EXECUTE_VERIFY.md`
5. Gmail execute+verify equivalent
6. `05_TRIGGER_WAKE_AND_DEPLOY.md`
7. `06_FIRST_LIVE_CLOSED_LOOP.md`

## Existing tools to reuse

- Supabase/Postgres = canonical persistence
- official TypeScript MCP SDK = remote tool surface
- Trigger.dev = durable wake/retry/background work
- Composio/direct provider APIs = app connectors/auth
- GitHub/Gmail/Calendar = first live sources
- existing ChatGPT connectors remain valid bootstrap operators
- Claude Code = implementation worker
- browser automation only where no API/MCP path exists

## Do NOT block V1 on

- LibreChat
- Firecrawl
- n8n
- Instructor
- FastMCP
- broader CRM coverage
- browser automation
- observability expansion
- marketplace packaging

These are post-receipt additions.

## Phase 1 exit condition

A real event must complete:

```text
external event
→ normalize
→ SYNC
→ NOW
→ PREP
→ approval gate
→ execute once
→ fresh external reread
→ VERIFY
→ RECEIPT
→ SETTLE
→ restart/fresh client
→ NOW advances
```

Do not proceed to Phase 2 until this passes.

---

# PHASE 2 — OPERATIONALIZE REALITY ONTOLOGY

Parent branch:
`operational-reality-v1`

Child priority:

## P0
1. `or/cognitimeexec-now`
2. `or/leverage-firewall`
3. `or/predictive-setup`

## P1
4. `or/predictive-maintenance`
5. `or/life-logistics-floor`
6. `or/attention-firewall`

Read:
- `operational-reality/PARENT_BRANCH_MAP.md`
- `operational-reality/OPERATIONAL_REALITY_CONTRACT.md`
- `operational-reality/LEVERAGE_POLICY.md`
- `operational-reality/CHILD_REGISTRY.yaml`
- each child branch contract

Do not merge a child until its acceptance receipt exists.

---

# P0.1 — COGNITIMEEXEC NOW

Implement the smallest compiler that converts current reality into one exact 0–10 minute action.

Output must always include:

```yaml
moment:
  workstream:
  transition:
  why_now:
  horizon_minutes: 10
  exact_action:
  surface:
  operator:
  prep_status:
  authority:
  can_execute_now:
  blocked_by:
  stop_after:
  receipt_required:
  if_finished_early:
  if_blocked:
  interrupt_if:
```

Forbidden outputs:
- "work on university"
- "continue Logistinfra"
- "do outreach"
- "study"
- any project-level vagueness

Acceptance:
- every result is immediately startable;
- waiting work excluded;
- <=1x non-essential labour excluded;
- exact surface and receipt present;
- state change recomputes route.

---

# P0.2 — LEVERAGE FIREWALL

Before any task reaches the human active queue, classify:

`KILL | AUTOMATE | DELEGATE | BATCH | FLOOR | KEEP`

Use:

```text
TLR =
expected future human minutes avoided/unlocked
/
(current human minutes + expected maintenance minutes)
```

## KILL
Optional, non-compounding, non-protective, <=1x work.

## AUTOMATE
Bounded, repeatable, reliably tool-executable.

## DELEGATE
Necessary but user-specific judgment is unnecessary.

## BATCH
Necessary repeated work dominated by setup/context-switching.

## FLOOR
Mandatory/protective/relationship-critical but low leverage.
Examples:
- university compliance;
- required admin;
- hygiene/getting ready;
- necessary travel prep;
- health/safety;
- important relationship commitments.

Compress these. Do not ignore them.

## KEEP
Human uniquely provides judgment, trust, negotiation, access, learning bottleneck removal, or high external consequence.

Acceptance:
- <=1x optional work cannot enter CogniTimeExec;
- observable state is not manually tracked twice;
- necessary recurring work gets an executor, batch, or floor;
- automation maintenance cost stays below labour removed.

---

# P0.3 — PREDICTIVE SETUP

Predict only 1–3 transitions ahead.

Safely pre-position:
- exact URL/site;
- repo/branch;
- files/artifacts;
- context packet;
- prompt/handoff;
- credentials/auth health;
- required physical items;
- acceptance condition;
- verifier.

Never:
- send;
- post;
- submit;
- purchase;
- merge;
- create external consequence based only on prediction.

Acceptance:
- selected work begins without context/site/file reconstruction;
- stale prep invalidates automatically;
- measured setup time declines.

---

# P1.1 — PREDICTIVE MAINTENANCE

Maintain only material operational surfaces:

V1:
- GitHub/CI;
- Gmail/Calendar connector health;
- Supabase/runtime health;
- Trigger.dev jobs;
- deployment health;
- active commitments/deadlines;
- unverified executions;
- stale waiting workstreams.

Contract:

```text
EXPECTED
→ OBSERVED
→ DELTA
→ MATERIAL?
→ bounded repair
→ RETEST
→ RECEIPT
```

No aesthetic maintenance.
No daily manual checklist where a health signal exists.

Acceptance:
- at least one degradation is detected before user discovery;
- non-material changes stay silent;
- repair is independently retested.

---

# P1.2 — LIFE LOGISTICS FLOOR

Cover only recurring mandatory friction first:

## University
- deadlines
- assessments
- required admin
- attendance/mandatory events
- source from Calendar/email/files
- no duplicate manual deadline list

## Getting ready
- default kits/checklists by destination/activity
- previous-window pre-stage
- replenish missing recurring items
- keep it minimal

## Admin/documents
- renewal/forms/payment/document requests
- exact source
- required fields
- due date
- submission verifier

Goal:

```text
detect
→ default/batch
→ pre-stage
→ one human checkpoint if required
→ execute
→ verify
→ disappear until next trigger
```

Acceptance:
- no mandatory obligation lost;
- recurring setup labour falls;
- floor work does not crowd out primary leverage work.

---

# P1.3 — ATTENTION FIREWALL

Classify inbound events as:

`WAKE_NOW | ROUTE_AS_WORK | BATCH_DIGEST | ARCHIVE/SUPPRESS | HUMAN_REVIEW`

Wake only when an event changes:
- admissibility;
- priority;
- commitment;
- access;
- production/security state;
- important relationship state;
- high-information correction.

Promotions/general feeds never preempt.

Acceptance:
- covered sources require no manual polling;
- important replies still preempt;
- duplicates collapse;
- low-value information remains retrievable without becoming active work.

---

# GMAIL→HUBSPOT RED-TEAM FINDINGS

Treat these as ONE workstream's evidence and falsification state.

Do NOT create new architecture branches for:
- HubSpot security;
- pricing;
- RevOps targeting;
- email parsing;
- payment;
- retention.

Canonical routing-relevant state only:

```yaml
hubspot_write:
  state: DEGRADED_OR_UNVERIFIED
  consequence: live pilot fulfillment may fail
  maintenance_transition: reauthorize + staging write test

market_offer:
  state: OUTREACH_LIVE
  uncertainties:
    - buyer pain unconfirmed
    - pricing/trust unverified
    - founder vs RevOps owner unverified

commercial_workstream:
  state: WAITING_ON_EXTERNAL
  wake_condition: substantive reply
```

Predictive setup candidate:
- restricted HubSpot Private App scope/security guide

But only prepare it when the workstream approaches:
`PROBLEM_CONFIRMED -> ACCESS_REQUIRED`

Do not let speculative prep preempt higher-value external work.

---

# DAILY HUMAN ATTENTION LAW

The user should increasingly supply only:

- intent;
- irreversible judgment;
- approvals;
- credentials/access;
- negotiation;
- high-value relationships;
- physical action;
- corrections when system reality is wrong.

Everything else should be pushed toward:
- existing connector;
- existing tool;
- existing OSS;
- existing repo component;
- automation;
- batch;
- default;
- predictive prep;
- predictive maintenance.

---

# GLOBAL V1 ACCEPTANCE

V1 is complete only when all are true:

- [ ] persistent canonical state survives restart;
- [ ] remote MCP client can call runtime;
- [ ] GitHub/Gmail/Calendar live reads update reality;
- [ ] GitHub and Gmail bounded writes can execute with approval;
- [ ] writes are independently verified;
- [ ] receipts settle durably;
- [ ] Trigger.dev wakes only on material state changes;
- [ ] waiting work is suppressed;
- [ ] CogniTimeExec always returns one exact 10-minute action or justified idle/prep;
- [ ] <=1x optional labour cannot enter human queue;
- [ ] mandatory low-leverage work is floored, not forgotten;
- [ ] likely next work is safely pre-staged;
- [ ] maintenance degradation creates bounded repair transitions;
- [ ] covered inbound sources do not require manual polling;
- [ ] fresh session resumes without reconstruction.

When all pass:

`V1 = COMPLETE`

Then STOP core infrastructure work.

---

# POST-V1 DEFAULT

Do not keep building Logistinfra internally.

Default loop:

```text
USE LOGISTINFRA
→ identify verified internal primitive
→ choose existing ecosystem
→ package minimally
→ externalize
→ obtain maintainer/user/customer receipt
→ feed evidence back
→ repeat
```

Likely surfaces:
- GitHub issues/PRs
- LangGraph / Browser Use / MCP ecosystem
- MCP Registry
- npm
- GitHub Marketplace
- OpenAI plugin surface
- VS Code marketplace
- HubSpot/n8n/Vercel integrations
- X/LinkedIn/Reddit/HN as proof amplification
- Microsoft/NVIDIA programs only after deployable proof

No marketplace work may preempt V1 completion unless it creates a live external receipt with higher immediate value.

---

# REQUIRED CLAUDE RETURN FORMAT

At every meaningful closure return:

```text
CURRENT VERIFIED STATE:
CURRENT BRANCH:
TARGET TRANSITION:
REUSED:
THIN_GLUE_ADDED:
TESTS:
LIVE VERIFICATION:
PROVES:
DOES_NOT_PROVE:
HUMAN_INPUT_REQUIRED:
LABOUR_REMOVED:
MAINTENANCE_INTRODUCED:
NEXT 10-MINUTE ACTION:
NEXT_BRANCH:
STOP/CONTINUE:
```

Do not return strategy prose unless a real blocker invalidates the execution contract.

BEGIN NOW with Phase 0 reconstruction, then execute the first dependency-correct missing seam.
