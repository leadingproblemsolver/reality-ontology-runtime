# n8n MCP Schema Continuity Analyzer

## Target

n8n issue #33864:
https://github.com/n8n-io/n8n/issues/33864

Reported behavior:

```text
typed MCP tool schema works
→ later tools/list emits {"type":"object"} with no properties
→ array/number arguments arrive as strings
→ server rejects them
```

The first thing worth proving is whether the schema collapse is actually present in repeated `tools/list` responses.

## Artifact

`analyzer.py` compares two MCP `tools/list` snapshots and classifies each tool as:

- `SCHEMA_COLLAPSED`
- `SCHEMA_RECOVERED`
- `SCHEMA_CHANGED`
- `UNCHANGED`
- `TOOL_ADDED`
- `TOOL_REMOVED`

It records which typed fields disappeared.

## Strong discriminator

If the same server endpoint emits:

```json
{"type":"object","properties":{"status":{"type":"array"},"limit":{"type":"number"}}}
```

and later emits:

```json
{"type":"object"}
```

for the same tool, the emitted schema itself has changed.

That materially strengthens a server/registry/cache-generation hypothesis.

If the server response stays typed but the client sends strings, the investigation should move client-side instead.

## Minimum capture protocol

Capture three snapshots:

1. **healthy** — immediately after a fresh session/connector when typed calls work;
2. **degraded** — immediately after the first typed-argument failure;
3. **fresh-session** — after fully starting a new client session.

For each snapshot preserve:

- timestamp;
- n8n version;
- MCP server/connector identity if available;
- session identity (opaque/redacted is fine);
- raw `tools/list` entries for affected tools.

Do not rely on screenshots if raw JSON can be exported.

## Hostile tests

The local test suite distinguishes:

1. full typed-properties collapse;
2. partial schema drift;
3. unchanged schema;
4. later schema recovery.

## Preproof contract

```yaml
claim: detect whether an MCP tool's emitted schema changes across tools/list snapshots
failure_case: typed properties disappear while the session remains live
input_fixture: before/after raw tools/list arrays
expected_behavior: exact per-tool schema continuity classification
hostile_test: full collapse vs partial drift vs unchanged vs recovered
receipt: deterministic diff listing lost typed fields
independent_reproduction: pytest tests/test_n8n_mcp_schema_continuity.py
claim_ceiling_before: diagnostic artifact
claim_ceiling_after_tests: deterministic schema-drift proof
next_external_test: reporter captures healthy + degraded + fresh-session snapshots
```

## Claim boundary

This artifact can prove that the schema **emitted in the supplied snapshots** changed.

It cannot by itself prove:
- which cache layer did it;
- whether the client transformed the response;
- whether a tool rename/version update triggered it;
- whether a race exists.

Those become the next hypotheses only after the snapshot boundary is established.
