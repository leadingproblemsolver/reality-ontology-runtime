# Immediately Usable Series

Branch: `immediatelyusable`

Purpose: turn the already-tested Logistinfra kernel into a standalone, immediately usable V1 with the fewest new moving parts.

## Rule

Do not redesign. Do not widen scope. Do not add a service unless the current step cannot pass without it.

Run these prompts in order:

1. `01_SUPABASE_STORE.md`
2. `02_MCP_HTTP_FACADE.md`
3. `03_LIVE_READ_BINDINGS.md`
4. `04_GITHUB_EXECUTE_VERIFY.md`
5. `05_TRIGGER_WAKE_AND_DEPLOY.md`
6. `06_FIRST_LIVE_CLOSED_LOOP.md`

Each step must:
- reuse current code;
- add only the missing seam;
- include negative tests;
- state PROVES / DOES_NOT_PROVE;
- stop after its acceptance gate passes.

## Stop condition for the whole series

A fresh external event enters the system, Logistinfra routes the correct transition, prepares the action, pauses for authority where required, executes once, independently verifies external reality, settles a receipt, and a fresh session routes the next transition without reconstruction.

After that: stop core infrastructure work.
