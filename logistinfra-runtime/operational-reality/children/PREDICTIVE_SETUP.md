# Predictive Setup — Structuralized Child Contract

Priority: P0
Parent: `operational-reality-v1`

## PURPOSE
Remove setup latency by pre-positioning everything safely predictable before the user reaches the transition.

## INVOKE_WHEN
- CogniTimeExec selects a likely successor;
- a waiting workstream has a probable response path;
- a calendar/deadline window approaches;
- a recurring routine is likely within the next horizon;
- PREP is requested.

## INPUTS
- current transition;
- top likely successor transitions;
- dependency graph;
- required surfaces/URLs/repos/files;
- auth/connection health;
- required context packet;
- prompts/handoffs;
- physical/digital materials;
- irreversible boundaries.

## RULES
1. Predict only 1–3 transitions ahead.
2. Prep only reversible/low-risk state.
3. Never send/post/submit/purchase/merge based on prediction.
4. Prefer cacheable retrieval and environment setup.
5. Invalidate prep when source state changes materially.
6. Do not precompute expensive work unless probability * labour saved exceeds maintenance cost.

## OUTPUT
```yaml
prep_packet:
  predicted_transition:
  probability_or_reason:
  required_surface:
  exact_entrypoint:
  context_refs:
  files_artifacts:
  repo_branch:
  auth_health:
  prompt_or_payload:
  physical_items:
  completed_prep:
  remaining_human_input:
  invalidation_condition:
  expires_at:
```

## EXISTING TOOLS
- connectors/APIs for live reads;
- GitHub;
- Gmail;
- Calendar;
- browser executor for no-API surfaces;
- Claude Code for repo setup;
- Firecrawl only where web acquisition is the actual bottleneck;
- local/browser bookmarks/deep links where appropriate.

## MVE
Predictive prep for:
1. next technical repo task;
2. next external reply path;
3. next hard calendar/university obligation;
4. one recurring getting-ready routine.

## ACCEPTANCE
- user can begin selected action without searching for the correct chat/site/file;
- prep never causes external consequence;
- stale prep is invalidated;
- measurable setup minutes decline;
- required credentials are surfaced before the action window.

## FAILURE
If prediction is weak or prep cost exceeds likely savings: do nothing.

## HANDOFF
Prep-status becomes an input to CogniTimeExec. Broken auth/surfaces create maintenance transitions.

## FIRST RECEIPT
A recurrent action starts from a pre-positioned packet and removes a measured setup step that previously required manual reconstruction.
