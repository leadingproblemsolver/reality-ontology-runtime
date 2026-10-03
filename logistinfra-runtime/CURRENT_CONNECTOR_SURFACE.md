# Current Connector Surface — Reuse Before Building

This file records connector/app surfaces already available to the current Logistinfra control plane. Gemini must treat these as the first integration candidates and must not propose custom adapters until it verifies that the existing surface cannot satisfy the required read/write/event/receipt contract.

## Tier 0 — directly relevant to Live Context / Reality / Navigation

### GitHub
Available now:
- repository/file/commit/branch/issue/PR/workflow reads;
- repository file writes, branches, commits, issues, PRs, comments/reviews;
- workflow run/job/log/artifact inspection and reruns.

Use for:
- repo state;
- technical workstreams;
- proof/receipt capture;
- implementation handoffs;
- CI verification.

### Gmail
Available now:
- search emails/IDs;
- read messages/threads/attachments;
- drafts;
- send/forward/archive/label actions.

Use for:
- external replies;
- commitments;
- follow-up state;
- market/buyer/employer receipts.

### Google Calendar
Available now:
- search/read events;
- availability;
- create/update/delete events;
- invitation response.

Use for:
- hard commitments;
- deadlines;
- wake windows;
- time-aware Moment Router state.

### Supabase
Available now:
- project/table/migration inspection;
- SQL execution;
- migrations;
- branches;
- Edge Function inspection/deployment;
- project URL/config retrieval.

Use for:
- canonical state;
- Reality Ontology persistence;
- workstream capsules;
- transitions;
- receipts;
- context packet registry.

### Slack
Available now:
- public/private search;
- channel/thread/canvas/list reads;
- message send/draft/schedule/edit;
- reminders and list/canvas creation.

Use for:
- optional low-friction Navigator output/notification surface;
- team/community signals when relevant;
- human approval/interruption delivery if selected.

## Tier 1 — Market Router / external consequence connectors already present

### Apollo
Prospecting/account/contact search and outbound-support data.

### Clay
Prospect/company discovery, enrichment, and engagement data.

### HubSpot
CRM contacts/companies/deals/tickets/engagements read/write.

### LinkedIn
Professional/profile lookup surface.

### Metricool
Social analytics, scheduled content, posting-time data, post creation/update.

### Stripe
Products/prices/payment links/payments/subscriptions management.

## Tier 2 — deployment surfaces already present

### Vercel
Projects/deployments/domains/environment/logs/deployment actions.

### Netlify
Build/deployment management.

## Current true gap

There is no platform-independent live connector in this runtime that exposes the full ChatGPT/Claude/Gemini conversation corpus as a canonical event stream.

Therefore do NOT pretend chat ingestion is already solved.

MVP order for chat sources:
1. exported/materialized chat files and the existing structuralization pack;
2. incremental file/folder ingestion with hashes/cursors;
3. any official provider export/API/connector that can be verified;
4. local user-authorized browser/desktop capture only if necessary;
5. browser automation only as a fallback.

Do not make undocumented private endpoints foundational.

## Reuse-first decision rule

For every required capability, Gemini must output one of:

- USE_EXISTING_CONNECTOR
- USE_EXISTING_REPO_COMPONENT
- COMPOSE_EXISTING_COMPONENTS
- BUILD_THIN_ADAPTER
- UNRESOLVED

Custom infrastructure is allowed only after the first three fail against an explicit acceptance test.
