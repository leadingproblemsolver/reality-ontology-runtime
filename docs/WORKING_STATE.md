# Working State

## Verified locally before publication

- 8 tests pass.
- The demo reaches `SETTLED_PROOF`.
- A fresh process reconstructs the same verified state from SQLite.
- A second run of the same settled transition returns `NOOP_ALREADY_SETTLED` rather than repeating the side effect.
- Verified-but-unsettled attempts after the demo: `0`.

## Current claim boundary

Proven in V0:
- local SQLite event/evidence state;
- deterministic projection;
- approval gating;
- bounded filesystem operator;
- independent reread verification;
- settlement receipt;
- assumption/signal/contradiction invalidation;
- restart recovery;
- idempotent settled transition handling.

Not yet proven:
- a real external API operator such as Gmail/GitHub/CRM;
- ambiguous timeout after an external side effect plus reread-before-retry reconciliation;
- concurrent/distributed workers;
- production persistence or scale.

## Next evidence event

Add exactly one real external operator and force an ambiguous timeout/crash boundary. Prove the runtime rereads external truth before retrying and produces one settled receipt without duplicate side effects.
