import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import type { NormalizedIssue, OpportunityScore } from "../types.js";

export const OpportunityScoreSchema = z.object({
  reproducibilityMinutes: z.number().min(0).max(600),
  boundedScope: z.boolean(),
  pythonRelevance: z.number().min(0).max(10),
  reliabilityRelevance: z.number().min(0).max(10),
  maintainerVerifiable: z.boolean(),
  setupBurden: z.enum(["low", "medium", "high"]),
  confidence: z.number().min(0).max(1),
  rationale: z.string().min(1),
  uncertainty: z.string().min(1),
  expectedInvariant: z.string().min(1),
  reproductionHypothesis: z.string().min(1),
  suggestedFirstTest: z.string().min(1),
  filesToInspect: z.array(z.string()).default([]),
  recommendedAction: z.string().min(1),
});

export interface LLMJudge {
  scoreIssue(issue: NormalizedIssue): Promise<OpportunityScore>;
}

export class LLMOutputError extends Error {
  constructor(
    message: string,
    public raw?: unknown,
  ) {
    super(message);
    this.name = "LLMOutputError";
  }
}

const RUBRIC_TOOL_NAME = "submit_opportunity_score";

const RUBRIC_TOOL_SCHEMA = {
  name: RUBRIC_TOOL_NAME,
  description: "Submit a structured score for whether a GitHub issue is a bounded, reproducible contribution opportunity.",
  input_schema: {
    type: "object" as const,
    properties: {
      reproducibilityMinutes: { type: "number", description: "Estimated minutes to reproduce the issue locally." },
      boundedScope: { type: "boolean", description: "Whether the fix is likely bounded to a small, identifiable area of code." },
      pythonRelevance: { type: "number", description: "0-10 relevance to Python code (browser-use is a Python project)." },
      reliabilityRelevance: { type: "number", description: "0-10 relevance to reliability/failure semantics." },
      maintainerVerifiable: { type: "boolean", description: "Whether a maintainer could plausibly verify a fix quickly." },
      setupBurden: { type: "string", enum: ["low", "medium", "high"] },
      confidence: { type: "number", description: "0-1 confidence in this assessment given available issue text." },
      rationale: { type: "string" },
      uncertainty: { type: "string", description: "What remains unknown or unverified from the issue text alone." },
      expectedInvariant: { type: "string", description: "The behavior/invariant that should hold once fixed." },
      reproductionHypothesis: { type: "string" },
      suggestedFirstTest: { type: "string" },
      filesToInspect: { type: "array", items: { type: "string" } },
      recommendedAction: { type: "string", enum: ["investigate", "ignore"] },
    },
    required: [
      "reproducibilityMinutes",
      "boundedScope",
      "pythonRelevance",
      "reliabilityRelevance",
      "maintainerVerifiable",
      "setupBurden",
      "confidence",
      "rationale",
      "uncertainty",
      "expectedInvariant",
      "reproductionHypothesis",
      "suggestedFirstTest",
      "filesToInspect",
      "recommendedAction",
    ],
  },
};

export class AnthropicJudge implements LLMJudge {
  private client: Anthropic;

  constructor(
    apiKey: string,
    private readonly model: string = "claude-sonnet-5",
  ) {
    this.client = new Anthropic({ apiKey });
  }

  async scoreIssue(issue: NormalizedIssue): Promise<OpportunityScore> {
    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 1024,
      tools: [RUBRIC_TOOL_SCHEMA],
      tool_choice: { type: "tool", name: RUBRIC_TOOL_NAME },
      messages: [
        {
          role: "user",
          content: [
            "Evaluate this GitHub issue from browser-use/browser-use as a candidate contribution opportunity.",
            "Judge strictly against: reproducibility within 60 minutes, bounded scope, Python relevance,",
            "reliability/failure-semantics relevance, maintainer-verifiability, and setup burden.",
            "Do not treat your own output as certain -- report genuine uncertainty.",
            "",
            `Title: ${issue.title}`,
            `URL: ${issue.url}`,
            `Labels: ${issue.labels.join(", ") || "(none)"}`,
            `Comments: ${issue.commentsCount}`,
            "",
            "Body:",
            issue.body || "(empty body)",
          ].join("\n"),
        },
      ],
    });

    const toolUse = response.content.find((block) => block.type === "tool_use");
    if (!toolUse || toolUse.type !== "tool_use") {
      throw new LLMOutputError("LLM response did not include the expected tool_use block", response);
    }

    const parsed = OpportunityScoreSchema.safeParse(toolUse.input);
    if (!parsed.success) {
      throw new LLMOutputError(
        `LLM output failed schema validation: ${parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ")}`,
        toolUse.input,
      );
    }

    return parsed.data;
  }
}
