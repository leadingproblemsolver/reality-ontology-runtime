# Predictive Maintenance — Structuralized Child Contract

Priority: P1
Parent: `operational-reality-v1`

## PURPOSE
Detect degradation before it causes interruption and create the smallest maintenance transition only when expected loss exceeds maintenance cost.

## INVOKE_WHEN
- health probe changes;
- credential expiry/reauth signal;
- CI/deployment failure;
- waiting state becomes stale;
- deadline/renewal approaches;
- repeated execution failure;
- proof/capability freshness crosses threshold.

## MAINTAINED SURFACES
V1 only:
- GitHub/CI;
- Gmail/Calendar connector health;
- Supabase/runtime health;
- Trigger.dev jobs;
- deployment health;
- active commitments/deadlines;
- unverified executions;
- stale waiting workstreams.

Later only if demanded:
- capability/skill decay;
- broader device/account maintenance.

## STATE MODEL
```text
EXPECTED
→ OBSERVED
→ DELTA
→ MATERIAL?
  no -> record silently
  yes -> maintenance transition
→ repair
→ retest
→ receipt
```

## OUTPUT
```yaml
maintenance:
  subject:
  expected_state:
  observed_state:
  delta:
  risk_if_ignored:
  time_to_failure:
  repair_cost:
  disposition:
  repair_transition:
  tool:
  retest:
  wake_condition:
```

## RULES
- no maintenance for aesthetics;
- no routine check if an existing health signal exists;
- batch maintenance where possible;
- preempt normal work only for material consequence;
- failed repair never settles itself.

## EXISTING TOOLS
Use provider health/state APIs, GitHub Actions, Vercel/Netlify logs, Supabase logs, Trigger.dev traces, connector auth status, Calendar/Gmail events.

## MVE
Implement five detectors:
1. CI failure;
2. connector/auth failure;
3. deployment unhealthy;
4. unverified execution older than threshold;
5. commitment entering action window.

## ACCEPTANCE
- at least one failure is detected before user discovery;
- non-material health changes remain silent;
- repair produces independent retest receipt;
- maintenance does not become a permanent daily checklist.

## FIRST RECEIPT
A simulated or harmless real degradation is detected, routed, repaired and retested without manual status checking.
