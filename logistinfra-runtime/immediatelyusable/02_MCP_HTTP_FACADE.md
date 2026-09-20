# Step 02 — MCP HTTP Facade

Act as Claude Code on branch `immediatelyusable`.

Prerequisite: Step 01 green.

## Objective

Expose the existing Logistinfra runtime as a standard remote MCP service without duplicating routing/business logic.

Use the official TypeScript MCP SDK and Streamable HTTP transport compatible with the current MCP specification.

## Expose only

- `now`
- `sync`
- `continue_workstream`
- `prep`
- `watch`
- `settle`
- `search_workstreams`
- `search_chats`
- `record_feedback`

Do NOT expose arbitrary database mutation.

`execute` may exist only as a bounded dispatcher into registered adapters with authority checks; do not bypass `runAutonomousCycle`.

## Mapping

- `now` -> existing route logic with current global mission/default selection
- `sync` -> existing sync
- `continue_workstream` -> route/reconstruct selected workstream
- `prep` -> compile Surface Action Packet
- `watch` -> set waiting/wake metadata through canonical state
- `settle` -> existing verified receipt settlement

## Requirements

- Zod/JSON schemas for every tool;
- read-only tools may run without approval;
- consequential writes still require authority;
- structured errors;
- health endpoint;
- stateless service process;
- all state in Supabase;
- no new agent framework.

## Acceptance

From a fresh standard MCP client:
1. connect;
2. call `sync`;
3. call `now`;
4. retrieve a real workstream;
5. call `prep`;
6. receive Surface Action Packet.

Restart server and repeat with same canonical state.

## Negative tests

- invalid tool payload;
- unknown workstream;
- forged/unverified receipt;
- unauthorized consequential execution;
- server restart.

## Return

```text
MCP_ENDPOINT:
TOOLS_EXPOSED:
TEST_CLIENT:
TESTS:
PROVES:
DOES_NOT_PROVE:
NEXT:
```

Stop when a fresh MCP client can route and prep from Supabase-backed state.
