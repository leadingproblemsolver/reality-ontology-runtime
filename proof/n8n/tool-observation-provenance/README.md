# n8n AI Agent Tool-Observation Provenance Analyzer

## Target

n8n issue #38870:
https://github.com/n8n-io/n8n/issues/38870

The reported failure is:

```text
tool executes successfully
→ tool execution contains real result
→ Agent intermediateSteps.observation == "\"\""
```

The useful question is not "did the tool run?"

It is:

> At what exact boundary does a known tool-call result stop matching the Agent observation?

## Current upstream source

Current `buildSteps()` constructs the observation from:

```ts
tool.data.data.ai_tool[0]
```

and intentionally falls back to:

```ts
JSON.stringify('')
```

when neither tool data nor error data is available.

Source:
`packages/@n8n/nodes-langchain/utils/agent-execution/buildSteps.ts`

That means the literal observation `""` is a strong discriminator: at step-building time, the corresponding engine response did not expose usable `ai_tool` data or an error in the shape `buildObservation()` expects.

It does **not** by itself prove why.

## Artifact

`analyzer.py` correlates:

```text
toolCallId
→ actionResponse
→ ai_tool payload presence
→ tool executionIndex
→ Agent executionIndex
→ intermediateSteps observation
```

It produces one of:

- `EMPTY_OBSERVATION_WITH_TOOL_DATA`
- `EMPTY_OBSERVATION_WITHOUT_TOOL_DATA`
- `OBSERVATION_PRESENT`
- `MISSING_ACTION_RESPONSE`
- `NO_TOOL_CALL_ID`

## Interpretation

### EMPTY_OBSERVATION_WITH_TOOL_DATA

Strongest signal.

The evidence bundle being analyzed contains both:
- a non-empty correlated tool payload;
- an empty Agent observation.

This localizes a mismatch at or after observation construction / serialization.

It still does not prove the exact implementation defect.

### EMPTY_OBSERVATION_WITHOUT_TOOL_DATA

The empty observation is consistent with current `buildObservation()`.

Next question:
why was `ai_tool` empty/missing at that point?

Timing, response assembly, tool output transfer, or earlier loss remain candidates.

### AGENT_BEFORE_TOOL ordering

If the saved evidence genuinely records the relevant Agent resume/read with a lower execution index than the tool result, timing becomes much more plausible.

But the exact Agent index used must correspond to the resume that consumed the tool response—not merely the original Agent invocation.

### MISSING_ACTION_RESPONSE

Correlation evidence is incomplete.

Do not call this "tool data loss."

## Hostile tests

The local tests prove the analyzer does not collapse these cases together:

1. tool data exists + observation empty → boundary mismatch
2. tool data missing + observation empty → upstream/timing gap
3. tool data exists + observation present → no anomaly
4. action response absent → correlation gap

## Preproof contract

```yaml
claim: correlate a tool result to the exact agent observation and classify the evidence boundary
failure_case: Agent observation is literal empty string while tool reportedly succeeded
input_fixture: correlated toolCallId + actionResponse + intermediateStep
expected_behavior: distinguish mismatch from missing upstream payload
hostile_test: empty observation with and without ai_tool payload
receipt: deterministic classification + execution-index ordering
independent_reproduction: pytest tests/test_n8n_tool_observation_provenance.py
claim_ceiling_before: diagnostic artifact
claim_ceiling_after_tests: deterministic evidence-localization tool
next_external_test: reporter provides one failing saved execution/export or exact correlated fields
```

## Exact evidence request for #38870

For one failing call, capture only:

1. `toolCallId`
2. `intermediateSteps[].observation`
3. correlated `actionResponse.data.data.ai_tool`
4. correlated tool `executionIndex`
5. Agent **resume** `executionIndex` that consumed that response

That five-field bundle is enough to collapse the main hypotheses without needing credentials or private business data.

## Claim boundary

This artifact does not claim a race condition exists.

It converts the issue from a timing narrative into an evidence-correlated boundary test.
