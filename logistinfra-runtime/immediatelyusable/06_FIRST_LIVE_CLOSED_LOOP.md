# Step 06 — First Live Closed Loop

Act as Claude Code / CTO brain on branch `immediatelyusable`.

Prerequisites: Steps 01–05 green.

## Objective

Prove one complete real Logistinfra loop. No feature work.

Use the already prepared LangGraph #8464 external-reply workstream unless current reality has produced a higher hard-preemption event.

## Required sequence

```text
live source event
→ normalized observation
→ SYNC
→ NOW
→ correct workstream/transition
→ PREP
→ approval gate
→ EXECUTE once
→ fresh external read
→ VERIFY
→ receipt
→ SETTLE
→ process restart / fresh MCP client
→ NOW
→ next transition, not previous one
→ WATCH if waiting on external reply
```

## Public write rule

Do not execute the LangGraph comment without explicit user approval bound to the exact prepared payload.

If approval is absent:
- stop at `AWAITING_APPROVAL`;
- return the exact Surface Action Packet.

If approval exists:
- execute exactly once;
- verify from GitHub;
- settle only after fresh readback.

## Acceptance checklist

- [ ] live source event ingested
- [ ] correct workstream selected
- [ ] waiting commercial lanes suppressed
- [ ] PREP packet produced
- [ ] approval enforced
- [ ] action executed once
- [ ] independent read verifies effect
- [ ] receipt stored in Supabase
- [ ] restart preserves settlement
- [ ] NEXT route advances
- [ ] workstream enters WATCH where appropriate

## Final output

```text
FIRST_LIVE_EVENT:
ROUTE:
ACTION:
APPROVAL:
EXECUTION:
VERIFICATION:
RECEIPT:
SETTLEMENT:
FRESH_SESSION_ROUTE:
WATCH_STATE:
PROVES:
DOES_NOT_PROVE:
CORE_INFRA_STATUS: STOP / CONTINUE
```

If all acceptance boxes pass:

`CORE_INFRA_STATUS: STOP`

Then do not add Firecrawl, n8n, LibreChat, browser automation, more adapters, or broader eval infrastructure until a live workstream demands one.
