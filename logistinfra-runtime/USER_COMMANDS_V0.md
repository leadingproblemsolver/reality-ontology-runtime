# User Command Contract V0

This file defines the minimum user-side interaction surface. It is intentionally not a new architecture.

## NOW
SYNC relevant live sources, suppress waiting/blocked work, and return exactly one highest-priority admissible transition plus one interruption lane.

## CONTINUE <workstream>
Recover last verified state, receipt, blocker, exact operator/surface/artifact and next transition without requiring the user to reconstruct history.

## PREP <transition>
Compile the Surface Action Packet: exact surface/URL, context, payload/prompt, auth health, first action, done_when, verifier and receipt contract. PREP creates no external consequence.

## EXECUTE
Run one approved bounded transition through the registered tool/model/browser/human surface. Always fresh-observe after action. Never equate tool success with outcome success.

## WATCH
Move a workstream out of active attention until its wake condition fires. Do not repeatedly resurface waiting-on-external work.

## SETTLE
Persist what became true, what remains unproven, the verified receipt, state delta, proof/access/capability delta, and the next transition.

## Surface Action Packet

```yaml
workstream:
transition:
current_state:
target_state:
surface:
entrypoint:
execution_mode:
authority:
auth_health:
context_refs:
payload_or_prompt:
first_action:
done_when:
verify_with:
receipt_required:
wake_condition:
```

This packet is the minimum bridge from routed intent to executable reality.
