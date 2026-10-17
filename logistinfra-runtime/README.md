# Logistinfra Runtime — Vertical Slice 01

This directory turns the Reality Ontology into a persistent background execution runtime.

## First live workload
Continuously inspect `browser-use/browser-use` GitHub issues for bounded, reproducible reliability bugs that can become real upstream contributions.

## Closed loop

scheduled trigger -> acquire issue data -> deterministic filter -> LLM score -> persist opportunity -> human approval -> prepare investigation -> record evidence

## Initial integrations
- GitHub API: source signals and later contribution receipts
- Trigger.dev: schedules/background jobs/retries
- Supabase/Postgres: canonical state and evidence
- LLM provider: bounded judgment only
- Browser Use / Playwright: later execution adapter after the first non-browser loop is verified

## Non-negotiables
- model output is not canonical truth
- raw provenance must be preserved
- reruns must be idempotent
- no external mutation without explicit approval
- tool success is not verified success
- failures must remain failures
- every recommendation must link back to source evidence

## First acceptance test
From a fresh process, run the pipeline against live or fixture GitHub issue data and persist a ranked opportunity whose source, filter decision, score, rationale, uncertainty, and recommended next action can all be reconstructed. Run twice and prove there is no duplicate side effect.

## Scope stop
Do not add browser automation, outreach, market scanning, dashboards, vector databases, graph databases, multi-agent chat, or generalized orchestration until this vertical slice passes its acceptance test.
