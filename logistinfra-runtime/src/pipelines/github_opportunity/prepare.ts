import type { StateStore } from "../../adapters/state-store.js";
import type { InvestigationPacket, NormalizedIssue, OpportunityScore } from "../../types.js";

export type PrepareResult =
  | { status: "awaiting_approval" }
  | { status: "declined" }
  | { status: "ready"; packet: InvestigationPacket };

/**
 * Builds the investigation packet from evidence already captured at
 * scoring time (no second LLM call). Only runs past the "ready" branch if a
 * human has explicitly approved the execution -- this is the human gate for
 * starting investigation, separate from any future external action.
 */
export async function prepareInvestigation(params: {
  executionId: string;
  store: StateStore;
}): Promise<PrepareResult> {
  const approval = await params.store.getLatestApproval(params.executionId);
  if (!approval) return { status: "awaiting_approval" };
  if (approval.decision !== "approved") return { status: "declined" };

  const execution = await params.store.getExecution(params.executionId);
  if (!execution) throw new Error(`unknown execution ${params.executionId}`);

  const opportunity = await params.store.getOpportunity(execution.opportunityId);
  if (!opportunity) throw new Error(`unknown opportunity ${execution.opportunityId}`);

  const signal = await params.store.getSignal(opportunity.signalId);
  if (!signal) throw new Error(`unknown signal ${opportunity.signalId}`);

  const issue = (signal.observation as { normalized?: NormalizedIssue }).normalized;
  if (!issue) throw new Error(`signal ${signal.id} is missing normalized issue data`);

  const rationale = opportunity.rationale as Partial<OpportunityScore>;

  const packet: InvestigationPacket = {
    repo: `${issue.owner}/${issue.repo}`,
    issueNumber: issue.number,
    issueUrl: issue.url,
    filesToInspect: rationale.filesToInspect ?? [],
    reproductionHypothesis: rationale.reproductionHypothesis ?? "(not captured)",
    expectedInvariant: rationale.expectedInvariant ?? "(not captured)",
    firstTest: rationale.suggestedFirstTest ?? "(not captured)",
  };

  await params.store.recordEvidence({
    executionId: params.executionId,
    signalId: signal.id,
    source: "investigation_prep",
    observation: { packet },
    proves: `investigation packet prepared for ${packet.repo}#${packet.issueNumber}`,
    doesNotProve: null,
  });

  await params.store.updateExecutionStatus(params.executionId, "completed");

  return { status: "ready", packet };
}
