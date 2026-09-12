import type { StateStore } from "../../adapters/state-store.js";
import type { ApprovalDecision, ExecutionRecord } from "../../types.js";

/**
 * Creates the human-decision gate for a recommended opportunity. Idempotent:
 * if an execution already exists for this opportunity (e.g. a rerun of the
 * scheduled scan), it is returned unchanged rather than duplicated.
 */
export async function proposeInvestigation(params: {
  opportunityId: string;
  store: StateStore;
}): Promise<ExecutionRecord> {
  const existing = await params.store.getExecutionForOpportunity(params.opportunityId);
  if (existing) return existing;

  return params.store.createExecution({
    opportunityId: params.opportunityId,
    action: "prepare_investigation",
    expectedTransition: "investigation packet persisted as evidence",
    approvalRequired: true,
    status: "awaiting_approval",
  });
}

/** Records the human's INVESTIGATE / IGNORE decision. No external action happens here. */
export async function decideInvestigation(params: {
  executionId: string;
  decision: ApprovalDecision;
  store: StateStore;
}): Promise<void> {
  const execution = await params.store.getExecution(params.executionId);
  if (!execution) throw new Error(`unknown execution ${params.executionId}`);

  await params.store.recordApproval({ executionId: params.executionId, decision: params.decision });
  await params.store.updateExecutionStatus(params.executionId, params.decision === "approved" ? "approved" : "rejected");
}
