import { describe, expect, it } from "vitest";
import { InMemoryStateStore } from "../src/adapters/state-store.js";
import { judgeSignals } from "../src/pipelines/github_opportunity/judge.js";
import type { NormalizedIssue } from "../src/types.js";
import { FixtureLLMJudge, InvalidOutputLLMJudge } from "./fakes.js";

function passingSignal(): { signalId: string; issue: NormalizedIssue } {
  return {
    signalId: "sig-1",
    issue: {
      sourceId: "browser-use/browser-use#501",
      owner: "browser-use",
      repo: "browser-use",
      number: 501,
      title: "Agent hangs on hidden iframe click",
      body: "repro steps",
      url: "https://github.com/browser-use/browser-use/issues/501",
      state: "open",
      labels: ["bug"],
      authorLogin: "someone",
      commentsCount: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  };
}

describe("judgeSignals", () => {
  it("scores every filtered-in signal on the happy path", async () => {
    const store = new InMemoryStateStore();
    const result = await judgeSignals({ passing: [passingSignal()], llm: new FixtureLLMJudge(), store });

    expect(result.scored.length).toBe(1);
    expect(result.failed.length).toBe(0);
    expect(result.scored[0]!.score.recommendedAction).toBe("investigate");
  });

  it("treats invalid LLM output as a persisted failure, not a guessed success", async () => {
    const store = new InMemoryStateStore();
    const result = await judgeSignals({ passing: [passingSignal()], llm: new InvalidOutputLLMJudge(), store });

    expect(result.scored.length).toBe(0);
    expect(result.failed.length).toBe(1);
    expect(result.failed[0]!.error).toMatch(/schema validation/);

    const evidence = store.listEvidence();
    expect(evidence.length).toBe(1);
    expect(evidence[0]!.source).toBe("llm_judge");
    expect(evidence[0]!.proves).toBeNull();
    expect(evidence[0]!.doesNotProve).toMatch(/LLM scoring failed/);
  });
});
