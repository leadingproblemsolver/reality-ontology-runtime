# Attention Firewall — Structuralized Child Contract

Priority: P1
Parent: `operational-reality-v1`

## PURPOSE
Prevent low-value inbound information, notifications and conversations from forcing context switches while preserving commitments, important relationships, access and high-information signals.

## INVOKE_WHEN
Any inbound event arrives from:
- email;
- Slack/community;
- GitHub;
- CRM;
- social/community feed where connected;
- browser/site notification;
- system alert.

## CLASSIFY EVENT
`WAKE_NOW | ROUTE_AS_WORK | BATCH_DIGEST | ARCHIVE/SUPPRESS | HUMAN_REVIEW`

## SIGNALS
- external actor waiting;
- deadline proximity;
- commitment/obligation;
- production/security consequence;
- access/opportunity;
- high-value relationship;
- current workstream relevance;
- primary data/correction;
- repetitive/noisy/promotional content.

## RULES
1. Classify interactions by state-changing relevance, not by a judgment of a person's worth.
2. Promotions/newsletters/general feeds never preempt.
3. Waiting-on-external replies wake only if they change admissibility/priority.
4. Low-priority useful information goes to digest, not NOW.
5. Duplicate alerts collapse to one source event.
6. User should not manually patrol inboxes for state changes already observable by connectors.

## OUTPUT
```yaml
attention_decision:
  event:
  source:
  disposition:
  reason:
  affected_workstream:
  priority_delta:
  user_interrupt: true|false
  digest_bucket:
  wake_condition:
  evidence:
```

## EXISTING TOOLS
Use Gmail/Slack/GitHub/CRM search/events, provider filters/labels, Trigger.dev event handling, and canonical workstream state.

## MVE
Apply to:
1. Gmail inbound;
2. GitHub comments/reviews;
3. system/runtime alerts.

Do not connect every social feed in V1.

## ACCEPTANCE
- irrelevant inbound cannot interrupt CogniTimeExec;
- important external replies still preempt correctly;
- duplicates collapse;
- no manual inbox polling is required for covered sources;
- digest items remain retrievable without becoming active work.

## FIRST RECEIPT
A mixed batch of live/synthetic inbound events results in only the state-changing event waking the user, with no missed commitment.
