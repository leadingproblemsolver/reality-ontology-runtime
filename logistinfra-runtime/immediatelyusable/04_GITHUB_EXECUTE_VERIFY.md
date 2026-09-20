# Step 04 — First Consequential Executor: GitHub

Act as Claude Code on branch `immediatelyusable`.

Prerequisites: Steps 01–03 green.

## Objective

Implement one real consequential adapter end-to-end.

Use GitHub issue-comment execution as the first production effect because:
- the connector/API is already available;
- the effect is inspectable;
- verification is cheap;
- the prepared LangGraph #8464 Surface Action Packet already exists.

## Adapter contract

Implement:

```ts
execute(request): ToolCallResult
verify(request, execution): VerificationResult
```

For issue comments:
- execution posts one approved exact comment;
- verification performs a fresh issue-comments read;
- verifier must match author + content digest + issue;
- exactly one matching effect is required;
- tool response alone is insufficient.

## Authority

Classify as `consequential_write`.

Without explicit approval:
- return `awaiting_approval`;
- perform no write.

Approval must bind to:
- transition ID;
- target issue;
- exact payload digest.

## Replay/idempotency

A retry after ambiguous execution must:
1. reread external state first;
2. settle if effect already exists exactly once;
3. not post again;
4. only execute if absence is proven and authority is still current.

## Test before live use

Use a harmless owned-repo fixture first.

Then prepare the existing packet:
`bootstrap/surface-packets/langgraph-8464-response.v0.json`

Do not post to LangGraph until explicit user approval is supplied.

## Acceptance

Owned fixture:
`PREPARED -> APPROVED -> EXECUTED -> fresh read -> VERIFIED -> SETTLED`

Fresh process then routes the next transition.

## Negative tests

- no approval;
- duplicate retry;
- API success but comment missing;
- ambiguous timeout;
- changed approval payload;
- two matching comments;
- revoked/expired authority if modeled.

## Return

```text
ADAPTER:
APPROVAL_CONTRACT:
FIXTURE_RECEIPT:
HOSTILE_TESTS:
PROVES:
DOES_NOT_PROVE:
READY_FOR_LANGGRAPH_APPROVAL: YES/NO
NEXT:
```

Stop before the public LangGraph write unless approval has been explicitly provided.
