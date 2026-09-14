import type { GithubIssuesClient, RawGithubIssue } from "../src/adapters/github.js";
import { GithubApiError } from "../src/adapters/github.js";
import type { LLMJudge } from "../src/adapters/llm.js";
import { LLMOutputError } from "../src/adapters/llm.js";
import type { NormalizedIssue, OpportunityScore } from "../src/types.js";

export class FixtureGithubClient implements GithubIssuesClient {
  constructor(private readonly issues: unknown[]) {}

  async listOpenIssues(): Promise<RawGithubIssue[]> {
    return this.issues as RawGithubIssue[];
  }
}

export class ThrowingGithubClient implements GithubIssuesClient {
  async listOpenIssues(): Promise<RawGithubIssue[]> {
    throw new GithubApiError("GitHub API returned 503 for browser-use/browser-use issues", 503);
  }
}

export function goodScoreFor(issue: NormalizedIssue): OpportunityScore {
  return {
    reproducibilityMinutes: 30,
    boundedScope: true,
    pythonRelevance: 9,
    reliabilityRelevance: 8,
    maintainerVerifiable: true,
    setupBurden: "low",
    confidence: 0.8,
    rationale: `Clear repro steps for issue #${issue.number}.`,
    uncertainty: "Have not confirmed against the current main branch.",
    expectedInvariant: "Clicking an element inside a hidden iframe returns ActionResult.error instead of hanging.",
    reproductionHypothesis: "The click handler awaits a frame attach event that never fires for display:none iframes.",
    suggestedFirstTest: "Assert ActionResult.error is returned within 5s for a click target inside a hidden iframe.",
    filesToInspect: ["browser_use/dom/service.py", "browser_use/controller/service.py"],
    recommendedAction: "investigate",
  };
}

/** Deterministic fake judge: every issue passed to it scores "good". */
export class FixtureLLMJudge implements LLMJudge {
  async scoreIssue(issue: NormalizedIssue): Promise<OpportunityScore> {
    return goodScoreFor(issue);
  }
}

export class InvalidOutputLLMJudge implements LLMJudge {
  async scoreIssue(): Promise<OpportunityScore> {
    throw new LLMOutputError('LLM output failed schema validation: confidence: Number must be less than or equal to 1');
  }
}
