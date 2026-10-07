# Target Dossier — n8n #33792

## Target

**Issue:** A single connected sub-node throwing in `supplyData()` fails the entire MCP Server Trigger / AI Agent request.

https://github.com/n8n-io/n8n/issues/33792

## Why this is the first upstream target

This is the cleanest bridge between:

- Logistinfra failure containment;
- Reality Ontology evidence/state boundaries;
- MCP;
- n8n AI Agent execution;
- public upstream engineering proof.

## Current source reconstruction

Failure site:
`packages/core/src/execution-engine/node-execution-context/utils/get-input-connection-data.ts`

The function iterates connected sub-nodes and calls:
`connectedNodeType.supplyData.call(context, itemIndex)`.

Current error behavior:
- configuration-node errors are re-thrown;
- other errors are wrapped as `NodeOperationError`;
- execution data is attached to the failing node;
- the parent call rejects.

Existing test file:
`packages/core/src/execution-engine/node-execution-context/utils/__tests__/get-input-connection-data.test.ts`

Existing tests already prove:
- one supplyData error rejects;
- configuration errors propagate;
- multiple healthy tools return.

## Missing regression

The key missing two-tool test is:

```text
parent AI/MCP node
├─ Tool A: supplyData throws
└─ Tool B: supplyData resolves
```

Question:
Does n8n intentionally require **all-or-nothing construction**, or should Tool B remain available when A fails?

That contract must come from maintainers before a core patch.

## Preproof test

Add a test conceptually equivalent to:

```ts
it('isolates one failing AI tool from healthy sibling tools', async () => {
  // connect failingTool + healthyTool
  // failingTool.supplyData rejects
  // healthyTool.supplyData resolves with healthy tool
  // desired semantics TBD by maintainer
})
```

Do not merge a guessed expectation into our own narrative.

## Maintainer coordination message

Use:

> I traced this on current master to `getInputConnectionData()` and its existing tests. Before touching `packages/core`, I want to confirm the intended contract.
>
> I can add a focused two-tool regression first:
>
> - Tool A throws from `supplyData()`
> - Tool B resolves normally
> - current behavior rejects the parent call
>
> Would you want the target behavior to be:
>
> **A)** preserve current all-or-nothing construction but improve the surfaced error, or  
> **B)** for `AiTool` fan-out specifically, isolate the failed tool and return the healthy sibling(s) with failure metadata recorded?
>
> If B is desired, I’ll keep the change scoped to the smallest connection type/call path the team prefers and add the regression before implementation.
>
> I’m asking first because your contribution guide explicitly requests coordination before `packages/core` changes.

## Receipt ladder

1. public maintainer reply = contract receipt
2. failing regression on agreed semantics = technical proof
3. passing patch = capability proof
4. upstream review = external judgment
5. merged PR = external acceptance
6. release inclusion = deployed ecosystem receipt

## Kill conditions

Do not patch if:
- maintainer says internal work is already underway;
- semantics should remain all-or-nothing;
- correct fix belongs outside core;
- issue is superseded by another internal change.

If killed, preserve the reconstruction and move immediately to S2 webhook idempotency template.
