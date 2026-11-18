# Prototype Gate — cross-system intake (v1)
This is a **read-only intake**, not a generator or certificate of production readiness.

## Run
```bash
python tools/prototype_gate.py /path/to/another/repository > prototype-report.json
pytest tests/test_prototype_gate.py
```
The JSON lists 10 areas: frontend, backend, persistence, tests, CI, deployment, identity, observability, documentation, configuration.

## Evidence and acceptance
- `NOT_DETECTED`: known file patterns did not match; capability might still exist elsewhere.
- `CANDIDATE_UNVERIFIED`: static file clue only; implementation, test pass, correctness, security and live deployments remain **unknown**.
- No claim of working software is permitted without actual tests and fresh target-system observation.
- Never promote a prototype to "DEPLOYED" because a config file or deployment command exists.

## Upgrade sequence for each prototype
1. Freeze one user journey and its input/output contract.
2. Run the gate against the original repo and record its exact commit SHA.
3. Pick the **first missing dependency**, not the largest code generator.
4. Add backend endpoint and validation; integration test with negative inputs.
5. Add durable state and migration; prove restart/reread and duplicate safety.
6. Connect frontend to real backend; test loading/error/retry states.
7. Test access control and data isolation. Keep secrets outside source.
8. Run CI and inspect deployed target independently.
9. Record external receipt and remaining unknowns in RealityStore.
10. Ask one real user to reproduce the journey and confirm acceptance.

## Non-goals and limits
Not a security audit, deployment tool, runtime test runner, vulnerability scanner or automatic code repair.
The generic pattern matching may miss unconventional layouts and may produce false positives. Results are a checklist for human confirmation.

Existing Logistinfra procurement behavior and RealityStore persistence are not modified.
