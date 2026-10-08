# n8n Public Proof Target Map

## Objective

Turn Logistinfra/Reality Ontology/CogniTime work into public, externally verifiable receipts inside one high-signal ecosystem.

Rank targets by:

1. **external acceptance potential**
2. **fit to our existing reliability/continuity machinery**
3. **smallest bounded contribution**
4. **speed to independent reproduction**
5. **speed to employment / paid work signal**
6. **low coordination overhead**

Do not optimize for issue count.

---

# Grade S — start here

## S1 — n8n #33792: MCP Server Trigger / AI Agent sub-node failure has whole-request blast radius

Issue:
https://github.com/n8n-io/n8n/issues/33792

Why S:
- direct overlap with Logistinfra's bounded-failure / recovery / tool-isolation thesis;
- public issue is already precise and source-grounded;
- exact core source and tests are identifiable;
- successful work demonstrates agent reliability, MCP understanding, testing discipline, and execution-boundary design;
- maps cleanly to later MCP reputation;
- directly legible to automation/AI employers.

Current upstream state:
- open;
- assigned to n8n AI/Cats teams;
- tracked internally as GHC-8896;
- core code change would touch `packages/core`, and n8n explicitly says to contact them before starting core changes.

Exact source:
`packages/core/src/execution-engine/node-execution-context/utils/get-input-connection-data.ts`

Existing regression surface:
`packages/core/src/execution-engine/node-execution-context/utils/__tests__/get-input-connection-data.test.ts`

Current behavior already tested:
- a supplyData error rejects the whole call;
- configuration-node errors propagate;
- multiple healthy tools return correctly.

Preproof contribution:
1. create a failing regression test with two AI tools:
   - tool A throws from `supplyData()`;
   - tool B resolves correctly.
2. prove current behavior aborts before B becomes usable.
3. define the smallest accepted behavior after maintainer guidance.
4. only then implement.

Strong receipt:
- maintainer confirms desired semantics;
- regression test accepted;
- patch/PR accepted or merged.

Claim ceiling before maintainer response:
> independently reconstructed the failure boundary and identified the exact regression surface.

Do not claim:
- that graceful degradation is definitely the desired core behavior;
- that a patch is upstream-acceptable before maintainers choose the contract.

### NOW
Prepare and post a pre-coordination comment with the exact two-tool regression test plan before touching core behavior.

---

## S2 — n8n Community: webhook idempotency / duplicate-side-effect patterns

Current public surfaces:
- https://community.n8n.io/t/webhook-events/317762
- https://community.n8n.io/t/stop-duplicate-side-effects-on-webhook-retries/315807

Why S:
- perfect mapping to Reality Ontology invariant: external uncertainty requires reread before retry;
- highly reusable;
- easy to package into a workflow template;
- immediate operator value;
- can produce public reproducible artifacts without waiting for core maintainer approval;
- paid workflow reliability work is abundant in the same community.

First contribution:
Build one n8n template:
`Webhook → atomic idempotency claim → processing state → side effect → durable receipt → completed state → retry-safe recovery`

Proof:
- same event delivered N times;
- exactly one external side effect;
- failed mid-run event can be resumed safely;
- output includes a durable receipt.

Strong receipt:
- public template;
- community operator reproduces it;
- real user reports duplicate prevention.

### NOW
This is the fastest independently shippable public proof surface while S1 waits on coordination.

---

# Grade A — strong but second

## A1 — n8n #31837: Webhook trigger firing multiple times

https://github.com/n8n-io/n8n/issues/31837

Fit:
duplicate execution / race / external receipt discipline.

Opportunity:
the reporter lacks a reliable reproduction. Our contribution should be a **diagnostic reproduction harness**, not a speculative fix.

Preproof:
- stable external `event_id`;
- correlate inbound request count vs execution count;
- isolate webhook-only vs connected-workflow behavior;
- record process/event-bus timestamps;
- distinguish provider retry from n8n duplication.

Strong receipt:
a deterministic or narrowed reproduction accepted by reporter/maintainer.

Risk:
high uncertainty; may consume time without reproducing.

---

## A2 — n8n #38396: process crashes while UI continues showing Running

https://github.com/n8n-io/n8n/issues/38396

Fit:
state truth vs declared execution state, crash recovery, durable resumption.

Opportunity:
build a minimal stale-execution detection / recovery contract:
`execution status + worker/process identity + heartbeat/fresh observation → trustworthy state`.

Strong proof:
- reproducible crash;
- stale-running state demonstrated;
- external truth reconciliation detects it.

Risk:
large product surface and potentially memory-management + UI + execution ownership boundaries.

Use after S1/S2 establish reputation.

---

## A3 — n8n #38870: tool executed successfully but AI Agent observation is empty

https://github.com/n8n-io/n8n/issues/38870

Fit:
handoff integrity, tool-result provenance, AI execution continuity.

Best contribution:
a trace-correlated reproducer proving:
`tool call id → subworkflow execution → actual output → agent observation`

Do not start with a fix.
First identify exact loss boundary with execution-index/call-id evidence.

Strong proof:
public trace/reproduction that collapses the hypothesis space.

---

## A4 — n8n #33864: typed MCP tool schemas collapse mid-session

https://github.com/n8n-io/n8n/issues/33864

Fit:
MCP state/version continuity, stale schema/cache invalidation.

Best contribution:
capture repeated `tools/list` snapshots across session lifecycle and tool rename/update boundary.

Proof:
exact before/after schema receipt showing where typed `properties` disappear.

This is especially valuable after S1 because the pair establishes an MCP reliability portfolio:
- runtime tool isolation;
- schema/state continuity.

---

# Grade B — useful, but avoid first

## B1 — n8n #39746: alwaysOutputData branch silently terminates

https://github.com/n8n-io/n8n/issues/39746

Why B:
good workflow-debugging proof but weaker direct fit to Logistinfra core.

Use for fast community debugging if a clean minimal workflow can be reproduced.

## B2 — n8n #39444: deactivated schedule registrations continue

https://github.com/n8n-io/n8n/issues/39444

Why B:
high fit to external-state authority and idempotency, but reporter is on old 1.x and current 2.x architecture appears to contain relevant structural protections.

Best contribution now is release/current-main verification, not a new patch.

## B3 — n8n #29726: webhook ACK blocked by concurrency queue

https://github.com/n8n-io/n8n/issues/29726

Why B:
excellent reliability problem but an existing PR has reportedly fixed the bottleneck.

Use as a proof-study / retrospective, not active engineering target.

---

# Employment / paid-work surface

The n8n Community Jobs category is currently active daily with:
- automation builder work;
- AI automation roles;
- paid QA/stress-testing;
- long-term n8n maintenance;
- technical implementation roles.

Conversion strategy:

`public reliability receipts → community recognition → targeted replies to paid requests where receipt is directly relevant`

Do not post generic "for hire" offers before 3–5 public technical receipts.

---

# Immediate execution order

## Block 1 — 25 min
S1 pre-coordination:
- finalize exact #33792 regression test shape;
- post concise maintainer question;
- settle with public comment receipt.

## Block 2 — 45–60 min
S2 template:
- build retry-safe webhook idempotency reference workflow/spec;
- create hostile tests;
- publish in our repo;
- then post to the two relevant community threads.

## Block 3
If S1 maintainers approve semantics:
- fork n8n;
- implement regression test first;
- patch only the agreed behavior;
- submit focused PR.

If no response:
- do not wait;
- continue S2 and A3/A4 evidence work.

---

# Proof engine rule

Every public contribution must produce at least two of:

1. external receiver;
2. independent reproduction;
3. hostile test;
4. accepted correction;
5. merged change;
6. repeated use;
7. public artifact;
8. paid consequence.

A comment without new evidence is not a proof object.
