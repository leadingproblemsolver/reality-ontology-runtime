import type { StateStore } from "../../adapters/state-store.js";
import { computeCompositeScore } from "../../policies/scoring.js";
import type { NormalizedIssue, OpportunityScore } from "../../types.js";
import type { ScoredSignal } from "./judge.js";

export interface PersistedOpportunity {
  opportunityId: string;
  signalId: string;
  issue: NormalizedIssue;
  score: OpportunityScore;
  composite: number;
  inserted: boolean;
}

/**
 * Persists one opportunity per scored signal, idempotent on signal_id.
 * Reruns update the row (in case the issue or scoring changed) rather than
 * creating a duplicate.
 */
export async function persistOpportunities(params: {
  scored: ScoredSignal[];
  store: StateStore;
}): Promise<PersistedOpportunity[]> {
  const results: PersistedOpportunity[] = [];

  for (const signal of params.scored) {
    const composite = computeCompositeScore(signal.score);

    const { id, inserted } = await params.store.upsertOpportunity({
      signalId: signal.signalId,
      target: `${signal.issue.owner}/${signal.issue.repo}#${signal.issue.number}`,
      problem: signal.issue.title,
      score: composite,
      rationale: { ...signal.score },
      uncertainty: signal.score.uncertainty,
      recommendedAction: signal.score.recommendedAction,
    });

    await params.store.recordEvidence({
      executionId: null,
      signalId: signal.signalId,
      source: "llm_judge",
      observation: { score: signal.score, composite },
      proves: `opportunity scored ${composite} (${inserted ? "created" : "updated"})`,
      doesNotProve: null,
    });

    results.push({
      opportunityId: id,
      signalId: signal.signalId,
      issue: signal.issue,
      score: signal.score,
      composite,
      inserted,
    });
  }

  return results;
}
