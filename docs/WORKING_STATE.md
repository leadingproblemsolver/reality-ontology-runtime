# Working State — V0

## Proven locally

- SQLite durable Reality Store initializes from an empty path.
- Evidence must exist before an event can reference it.
- Current object state is reconstructed from event history.
- Universal truth ladder blocks unsupported `DEPLOYED` promotion.
- L2 external/consequential operators are blocked without explicit approval.
- Execute and verify are separate stages.
- Successful verified runs persist an evidence receipt, event, settlement receipt, and `SETTLED` attempt.
- Fresh `RealityStore` process reconstructs the final state and context.
- Strong contradictory reality signals invalidate dependent decisions and remove them from active context.
- Canonical relations require evidence provenance.
- Re-running an already settled demo transition becomes a no-op rather than repeating the side effect.

## Not yet claimed

- No real Gmail/GitHub/browser/CRM operator is implemented.
- No production database migration framework.
- No concurrent-worker / locking proof.
- No crash-in-the-middle recovery proof between external mutation and verification.
- No real external system has yet been driven through this runtime.
- No LLM planner is integrated; deliberately, the truth path has no model dependency.
- No benchmark or production-scale evidence.

## Next evidence event

Implement **one real external operator** against a reversible/low-blast-radius workflow, force the ambiguous timeout case, then prove:

`execute may have happened → local receipt missing → reread external state → no duplicate retry → evidence → settlement → restart recovery`

That is the next highest-information transition because it tests the most dangerous invariant currently covered only by contract/tests, not a live external system.
