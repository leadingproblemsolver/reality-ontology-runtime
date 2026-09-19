import type { LLMJudge } from "../../adapters/llm.js";
import type { StateStore } from "../../adapters/state-store.js";
import type { OpportunityScore } from "../../types.js";
import type { AcquiredSignal } from "./scout.js";

export interface ScoredSignal extends AcquiredSignal {
  score: OpportunityScore;
}

export interface JudgeFailure extends AcquiredSignal {
  error: string;
}

export interface JudgeResult {
  scored: ScoredSignal[];
  failed: JudgeFailure[];
}

/**
 * Runs the LLM judge over deterministically-filtered signals only. Invalid
 * or missing structured output is a persisted failure for that signal, not a
 * guessed-into-shape success and not an aborted run.
 */
export async function judgeSignals(params: {
  passing: AcquiredSignal[];
  llm: LLMJudge;
  store: StateStore;
}): Promise<JudgeResult> {
  const scored: ScoredSignal[] = [];
  const failed: JudgeFailure[] = [];

  for (const signal of params.passing) {
    try {
      const score = await params.llm.scoreIssue(signal.issue);
      scored.push({ ...signal, score });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      failed.push({ ...signal, error: message });
      await params.store.recordEvidence({
        executionId: null,
        signalId: signal.signalId,
        source: "llm_judge",
        observation: { error: message },
        proves: null,
        doesNotProve: `LLM scoring failed or returned invalid output: ${message}`,
      });
    }
  }

  return { scored, failed };
}
