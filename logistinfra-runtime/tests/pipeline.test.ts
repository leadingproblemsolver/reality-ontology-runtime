import { describe, expect, it } from "vitest";
import { InMemoryStateStore } from "../src/adapters/state-store.js";
import { runOpportunityScan } from "../src/pipelines/github_opportunity/pipeline.js";
import { buildFixtureIssues, EXPECTED_PASSING_ISSUE_NUMBERS } from "./fixtures/browser-use-issues.js";
import { FixtureGithubClient, FixtureLLMJudge, ThrowingGithubClient } from "./fakes.js";

describe("runOpportunityScan (acceptance)", () => {
  it("produces a persisted, ranked, fully reconstructable opportunity from fixture GitHub data", async () => {
    const store = new InMemoryStateStore();
    const githubClient = new FixtureGithubClient(buildFixtureIssues());
    const llm = new FixtureLLMJudge();

    const result = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });

    expect(result.status).toBe("ok");
    if (result.status !== "ok") throw new Error("unreachable");

    expect(result.filteredInCount).toBe(EXPECTED_PASSING_ISSUE_NUMBERS.length);
    expect(result.opportunities.length).toBe(EXPECTED_PASSING_ISSUE_NUMBERS.length);
    expect(result.recommended).not.toBeNull();
    expect(result.recommended!.issue.number).toBe(EXPECTED_PASSING_ISSUE_NUMBERS[0]);
    expect(result.executionId).not.toBeNull();

    // --- reconstruct the recommendation purely from persisted state ---
    const opportunity = await store.getOpportunity(result.recommended!.opportunityId);
    expect(opportunity).not.toBeNull();
    const signal = await store.getSignal(opportunity!.signalId);
    expect(signal).not.toBeNull();
    expect((signal!.observation as { raw: unknown }).raw).toBeTruthy(); // raw source payload preserved

    const evidenceForSignal = store.listEvidence().filter((e) => e.signalId === signal!.id);
    const filterEvidence = evidenceForSignal.find((e) => e.source === "deterministic_filter");
    const judgeEvidence = evidenceForSignal.find((e) => e.source === "llm_judge" && e.proves);

    expect(filterEvidence?.proves).toBe("issue passed deterministic filter");
    expect(judgeEvidence?.proves).toMatch(/opportunity scored/);
    expect(opportunity!.rationale).toBeTruthy();
    expect(opportunity!.uncertainty).toBeTruthy();
    expect(opportunity!.recommendedAction).toBeTruthy();

    const execution = await store.getExecution(result.executionId!);
    expect(execution?.status).toBe("awaiting_approval");
    expect(execution?.approvalRequired).toBe(true);
  });

  it("re-running the same scan does not duplicate signals, opportunities, or executions", async () => {
    const store = new InMemoryStateStore();
    const githubClient = new FixtureGithubClient(buildFixtureIssues());
    const llm = new FixtureLLMJudge();

    const first = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });
    const second = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });

    expect(first.status).toBe("ok");
    expect(second.status).toBe("ok");
    if (first.status !== "ok" || second.status !== "ok") throw new Error("unreachable");

    expect(store.listSignals().length).toBe(first.signalsAcquired);
    expect(store.listOpportunities().length).toBe(first.opportunities.length);
    expect(store.listExecutions().length).toBe(1);
    expect(second.executionId).toBe(first.executionId);
    expect(second.recommended!.opportunityId).toBe(first.recommended!.opportunityId);
  });

  it("returns ok with no recommendation when nothing survives the deterministic filter", async () => {
    const store = new InMemoryStateStore();
    const onlyNoise = buildFixtureIssues().filter((issue) => issue.number !== 501); // drop the one qualifying issue
    const githubClient = new FixtureGithubClient(onlyNoise);
    const llm = new FixtureLLMJudge();

    const result = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });

    expect(result.status).toBe("ok");
    if (result.status !== "ok") throw new Error("unreachable");
    expect(result.opportunities).toEqual([]);
    expect(result.recommended).toBeNull();
    expect(result.executionId).toBeNull();
  });

  it("persists failure as failure when GitHub acquisition fails outright, instead of a false success", async () => {
    const store = new InMemoryStateStore();
    const githubClient = new ThrowingGithubClient();
    const llm = new FixtureLLMJudge();

    const result = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });

    expect(result.status).toBe("failed");
    if (result.status !== "failed") throw new Error("unreachable");
    expect(result.error).toMatch(/503/);

    const runFailureEvidence = store.listEvidence().find((e) => e.source === "pipeline_run");
    expect(runFailureEvidence).toBeTruthy();
    expect(runFailureEvidence?.doesNotProve).toMatch(/scan run failed/);
    expect(runFailureEvidence?.proves).toBeNull();
  });
});
