# Economic Execution Plane — Logistinfra + CogniTime

## Purpose

Bind existing model workers and CogniTime to the current Logistinfra runtime without creating another router, scheduler, memory system, or authority layer.

## Dependency order

```text
LIVE REALITY
  -> Reality Ontology / Continuity state
  -> Market Router (economic priority)
  -> Moment Router (one admissible transition now)
  -> capability selector
  -> worker/tool adapter
  -> execute
  -> fresh observe
  -> verify
  -> receipt
  -> SETTLE
  -> CogniTime session ledger / next bounded block
```

CogniTime is downstream of routing and upstream of human execution timing. It does not decide which project deserves capital.

## CogniTime contract

Input is only transitions already admitted by Logistinfra:

```yaml
objective:
success_metric:
available_minutes:
constraints:
transitions:
  - id:
    action:
    workstream:
    expected_receipt:
    leverage: 1-5
    urgency: 1-5
    confidence: 1-5
    minutes:
    dependency:
```

Output must preserve the existing `cognitime.plan.v1` semantics:

- ordered execution phases;
- exact next action;
- bounded time blocks;
- session metrics;
- Markdown / JSON / CSV / ICS exports;
- restart cue.

## 25-minute runtime block

Each block is one transition attempt, not a topic.

```text
00:00-00:30  SYNC / load current receipt + done_when
00:30-03:30  PREP / open exact surface, payload, verifier
03:30-20:00  EXECUTE / perform the bounded transition
20:00-22:00  VERIFY + SETTLE / capture receipt, state delta, blocker
22:00-25:00  EXTERNALIZE / reusable proof or exact restart cue
```

Twenty minutes remains the minimum useful execution slice; the default operating block is 25 minutes so verification and state transfer are not squeezed out.

A block is valid only if it produces at least one of:

- REALITY: outreach, conversation, feedback, observation;
- PROOF: artifact, demo, analysis, deployment;
- LEVERAGE: automation, reusable system, knowledge capture.

For market-facing work, prefer a direct external receipt over internal leverage work.

## Worker routing

The canonical registry is `live/worker_registry.v1.json`.

Transitions may use exact adapters:

```json
{ "toolRefs": ["tool:github.write"] }
```

or capabilities:

```json
{ "toolRefs": ["cap:code.execute"] }
```

Capability selection is deterministic and expandable: adding a registered adapter with the required capability makes it eligible without changing the transition schema.

## Hard boundaries

- models are workers, not authorities;
- deterministic code wins over LLM calls where it already solves the task;
- a model never settles a transition from its own success response;
- consequential writes keep existing approval gates;
- external state must be freshly reread before settlement;
- no provider is allowed to become canonical memory;
- no new product work before a live receipt justifies it.

## $10M relevance

The runtime optimizes for the only sequence that can compound toward the target:

```text
observed pain
-> reachable buyer/operator
-> smallest intervention
-> external receipt
-> proof
-> paid/referred/merged/use signal
-> repeatable distribution
-> automation only after repetition
```

Model cost savings matter only after this sequence is producing market feedback. The economic router therefore minimizes model spend subject to preserving receipt quality; it does not maximize token throughput.
