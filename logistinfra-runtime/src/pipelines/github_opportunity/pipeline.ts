import type { GithubIssuesClient } from "../../adapters/github.js";
import type { LLMJudge } from "../../adapters/llm.js";
import type { StateStore } from "../../adapters/state-store.js";
import type { FilterConfig } from "../../policies/filtering.js";
import { proposeInvestigation } from "./approval.js";
import { filterSignals } from "./filter.js";
import { judgeSignals } from "./judge.js";
import { persistOpportunities, type PersistedOpportunity } from "./persist.js";
import { rankOpportunities } from "./rank.js";
import { acquireAndPersistSignals } from "./scout.js";

export interface ScanOk {
  status: "ok";
  signalsAcquired: number;
  malformedCount: number;
  filteredInCount: number;
  filteredOutCount: number;
  scoredCount: number;
  judgeFailedCount: number;
  opportunities: PersistedOpportunity[];
  recommended: PersistedOpportunity | null;
  executionId: string | null;
}

export interface ScanFailed {
  status: "failed";
  error: string;
}

export type ScanResult = ScanOk | ScanFailed;

/**
 * The full closed loop for one repo:
 * acquire -> deterministic filter -> LLM score -> persist -> rank ->
 * propose the top opportunity for human approval.
 *
 * Never throws for ordinary operational failures -- those are captured as a
 * persisted `pipeline_run` evidence row and returned as status "failed" so a
 * caller (CLI, Trigger.dev task) can surface it without an uncaught crash
 * silently becoming a false "success".
 */
export async function runOpportunityScan(params: {
  owner: string;
  repo: string;
  githubClient: GithubIssuesClient;
  llm: LLMJudge;
  store: StateStore;
  filterConfig?: FilterConfig;
}): Promise<ScanResult> {
  const startedAt = new Date();

  try {
    const { signals, malformed } = await acquireAndPersistSignals({
      owner: params.owner,
      repo: params.repo,
      githubClient: params.githubClient,
      store: params.store,
    });

    const { passing, rejected } = await filterSignals({
      signals,
      store: params.store,
      config: params.filterConfig,
    });

    const { scored, failed } = await judgeSignals({ passing, llm: params.llm, store: params.store });

    const opportunities = await persistOpportunities({ scored, store: params.store });
    const ranked = rankOpportunities(opportunities);
    const recommended = ranked[0] ?? null;

    let executionId: string | null = null;
    if (recommended) {
      const execution = await proposeInvestigation({ opportunityId: recommended.opportunityId, store: params.store });
      executionId = execution.id;
    }

    return {
      status: "ok",
      signalsAcquired: signals.length,
      malformedCount: malformed.length,
      filteredInCount: passing.length,
      filteredOutCount: rejected.length,
      scoredCount: scored.length,
      judgeFailedCount: failed.length,
      opportunities: ranked,
      recommended,
      executionId,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await params.store.recordEvidence({
      executionId: null,
      signalId: null,
      source: "pipeline_run",
      observation: { error: message, startedAt: startedAt.toISOString(), owner: params.owner, repo: params.repo },
      proves: null,
      doesNotProve: `scan run failed: ${message}`,
    });
    return { status: "failed", error: message };
  }
}
