---
name: operate
description: Execute a bounded Logistinfra/Reality Ontology workstream using verified canonical state. Use for NOW, CONTINUE, PREP, EXECUTE, WATCH and SETTLE.
---

Operation: $ARGUMENTS

1. Read repository CLAUDE.md, docs/CLAUDE_LOCAL_CUTOVER.md and the SessionStart projection. The hook is READ ONLY, not an external source sync.
2. Read actual local evidence with `python -m reality_ontology.cli --db .runtime/reality.db verify-invariants` and `python -m reality_ontology.cli --db .runtime/reality.db next`. No DB or mission is UNINITIALIZED, never falsely "all done".
3. CONTINUE: locate the exact latest verified state, transition, receipt, blocker, workstream owner and source. Seed JSON is only a locator, not a live read. Check permissions for each external source independently.
4. NOW: choose one 0–10 minute dependency-correct transition with observed prerequisite, exact tool/human, authority, postcondition, independent verifier, stop rule and inspectable receipt. If no mission exists, first create an evidence-backed spec matching the `next-start` schema and verify source state before starting it. Do not fill stale fields by guessing.
5. PREP: prepare exact `source → action → target → receipt` with access health and approval class. PREP never counts as a real external action.
6. EXECUTE: use the existing applicable CLI/API/MCP path. Human approval first for consequential writes. Confirm fresh external state separately from a tool acknowledgement. Do not make duplicate send or write on rerun.
7. SETTLE: only settle verified outcomes with the existing `next-settle` CLI. `RECEIPT`, `CAPABILITY_GAIN` and `FALSIFIED_HYPOTHESIS` require inspected receipt locator; `BLOCKED` and `EXPLICIT_KILL` must be described literally. Do not settle the same event into TS JSON and Python SQLite independently.
8. Open fresh Python process; verify canonical result and rerun/idempotence behavior. Report what actually changed, source of evidence, whose access changed, exact next external event.

Always show `VERIFIED`, `OBSERVED`, `UNPROVEN`, or `BLOCKED` separately. Avoid designing another dashboard, queue, memory system, or scheduler.
