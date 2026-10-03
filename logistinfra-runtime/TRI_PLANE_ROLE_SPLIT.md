# Logistinfra Tri-Plane Role Split

## Canonical split

- **Gemini = Integration + Context Plane** — discover/connect sources, ingest chats/files/external events, preserve provenance, normalize/synchronize reality, structuralize chats into operators, compile minimum context bundles.
- **GPT = MVExec + Decision Plane** — consume Gemini context, run Moment Router, select one dependency-correct next transition, execute through connected tools where authorized, or emit a bounded production handoff.
- **Claude = Production Assembly Plane** — consume bounded handoff, implement/test/deploy/harden the required code path, independently verify the state transition, and emit a machine-readable receipt.

Closed loop:

```text
sources + chats + external events
→ Gemini context/integration plane
→ context bundle + reality snapshot
→ GPT MVExec
→ direct execution OR production handoff
→ Claude assembly
→ verification receipt
→ Gemini re-ingestion
→ updated reality
→ next `li now`
```

## Non-negotiable handoffs

Gemini → GPT: `CONTEXT_BUNDLE` + `REALITY_SNAPSHOT` + `OPERATOR_REGISTRY` + `INTEGRATION_STATUS`.

GPT → Claude: `PRODUCTION_HANDOFF` containing exact objective, verified state, required behavior, invariants, authority, failure behavior, acceptance tests, hostile tests, stop condition, and receipt required.

Claude → Gemini/GPT: `VERIFICATION_RECEIPT` containing implemented/tested/runtime observations/state delta/failed-or-unproven/PROVES/DOES_NOT_PROVE/next dependency.

## Constraint

No plane is allowed to silently re-open the other plane's settled work. It may only escalate when evidence is stale, contradictory, impossible to implement, or outside authority.
