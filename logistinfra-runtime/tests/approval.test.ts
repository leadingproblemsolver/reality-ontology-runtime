import { describe, expect, it } from "vitest";
import { InMemoryStateStore } from "../src/adapters/state-store.js";
import { decideInvestigation, proposeInvestigation } from "../src/pipelines/github_opportunity/approval.js";
import { prepareInvestigation } from "../src/pipelines/github_opportunity/prepare.js";
import { goodScoreFor } from "./fakes.js";
import type { NormalizedIssue } from "../src/types.js";

async function seedOpportunity(store: InMemoryStateStore) {
  const issue: NormalizedIssue = {
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
  };
  const { id: signalId } = await store.upsertSignal({
    source: "github",
    sourceId: issue.sourceId,
    sourceUrl: issue.url,
    observation: { normalized: issue, raw: {} },
  });
  const score = goodScoreFor(issue);
  const { id: opportunityId } = await store.upsertOpportunity({
    signalId,
    target: `${issue.owner}/${issue.repo}#${issue.number}`,
    problem: issue.title,
    score: 0.9,
    rationale: { ...score },
    uncertainty: score.uncertainty,
    recommendedAction: score.recommendedAction,
  });
  return { signalId, opportunityId };
}

describe("proposeInvestigation", () => {
  it("is idempotent: a second proposal for the same opportunity returns the same execution", async () => {
    const store = new InMemoryStateStore();
    const { opportunityId } = await seedOpportunity(store);

    const first = await proposeInvestigation({ opportunityId, store });
    const second = await proposeInvestigation({ opportunityId, store });

    expect(second.id).toBe(first.id);
    expect(store.listExecutions().length).toBe(1);
  });
});

describe("prepareInvestigation", () => {
  it("refuses to prepare a packet before a human decision exists", async () => {
    const store = new InMemoryStateStore();
    const { opportunityId } = await seedOpportunity(store);
    const execution = await proposeInvestigation({ opportunityId, store });

    const result = await prepareInvestigation({ executionId: execution.id, store });

    expect(result.status).toBe("awaiting_approval");
    expect(store.listEvidence().length).toBe(0);
  });

  it("does not prepare a packet when the human rejects the opportunity", async () => {
    const store = new InMemoryStateStore();
    const { opportunityId } = await seedOpportunity(store);
    const execution = await proposeInvestigation({ opportunityId, store });

    await decideInvestigation({ executionId: execution.id, decision: "rejected", store });
    const result = await prepareInvestigation({ executionId: execution.id, store });

    expect(result.status).toBe("declined");
  });

  it("prepares a reconstructable investigation packet once approved, and never mutates GitHub", async () => {
    const store = new InMemoryStateStore();
    const { opportunityId } = await seedOpportunity(store);
    const execution = await proposeInvestigation({ opportunityId, store });

    await decideInvestigation({ executionId: execution.id, decision: "approved", store });
    const result = await prepareInvestigation({ executionId: execution.id, store });

    expect(result.status).toBe("ready");
    if (result.status !== "ready") throw new Error("unreachable");
    expect(result.packet.repo).toBe("browser-use/browser-use");
    expect(result.packet.issueNumber).toBe(501);
    expect(result.packet.filesToInspect.length).toBeGreaterThan(0);

    const updated = await store.getExecution(execution.id);
    expect(updated?.status).toBe("completed");

    const evidence = store.listEvidence().find((e) => e.source === "investigation_prep");
    expect(evidence?.proves).toMatch(/investigation packet prepared/);
  });
});
