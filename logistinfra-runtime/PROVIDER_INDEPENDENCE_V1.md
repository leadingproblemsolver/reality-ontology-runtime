# Provider Independence Layer V1

## What changed

The runtime no longer needs transition schemas to name Claude/OpenAI/Gemini/DeepSeek directly.

Transitions select capabilities:

```json
{ "toolRefs": ["cap:research.synthesize"] }
```

The resolver selects a configured adapter deterministically by:

```text
transition selector order
→ lowest costRank
→ highest qualityRank
→ stable adapter ref
```

## Runtime-owned seams

- `src/autonomy/resolver.ts` — capability resolution
- `src/autonomy/model-worker.ts` — provider-neutral worker adapter
- `src/autonomy/providers.ts` — provider invocation implementations
- `src/autonomy/worker-factory.ts` — environment-configured worker registry
- `live/worker_registry.v1.json` — policy/intent registry

## Supported provider invocation surfaces

- Anthropic Messages API
- OpenAI Responses API
- Gemini generateContent REST API
- OpenAI-compatible chat endpoint for DeepSeek-style providers

Providers are workers only. They do not own:
- canonical truth;
- routing;
- approvals;
- external settlement.

## Proof boundary

A model worker adapter can prove only:

```text
an inspectable artifact was produced
+
its content hash was independently recomputed
```

It explicitly does NOT prove:
- semantic correctness;
- repo mutation;
- deployment;
- send/post;
- payment;
- external state change.

Those require dedicated surface adapters and fresh external rereads.

## Independence achieved

A reasoning/research/artifact transition may move between providers without changing:
- workstream;
- transition schema;
- routing;
- receipt semantics.

## Still missing for full independence

1. runtime entrypoint that constructs the configured worker map automatically;
2. live provider credential smoke test for at least two providers;
3. dedicated external surface adapters for GitHub/Gmail/Calendar/browser/API actions;
4. standalone persistence/event ingestion outside the ChatGPT control plane;
5. remote MCP/API facade.

## Next dependency-correct layer

Do NOT add another agent framework.

Bind the worker factory into the runtime entrypoint, then prove:

```text
same capability transition
→ provider A executes
→ receipt
→ disable A
→ provider B executes
→ same transition schema
→ receipt
```

After that, move immediately to external surface independence.
