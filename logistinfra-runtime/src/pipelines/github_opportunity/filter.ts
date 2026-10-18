import type { StateStore } from "../../adapters/state-store.js";
import { DEFAULT_FILTER_CONFIG, evaluateFilter, type FilterConfig } from "../../policies/filtering.js";
import type { AcquiredSignal } from "./scout.js";

export interface FilterResult {
  passing: AcquiredSignal[];
  rejected: Array<AcquiredSignal & { reasons: string[] }>;
}

/**
 * Applies the deterministic filter to every acquired signal and persists the
 * decision (pass or reject, with reasons) as evidence before any LLM call is
 * made -- this is what makes "why was X selected/rejected" reconstructable
 * without re-running the judge.
 */
export async function filterSignals(params: {
  signals: AcquiredSignal[];
  store: StateStore;
  config?: FilterConfig;
}): Promise<FilterResult> {
  const config = params.config ?? DEFAULT_FILTER_CONFIG;
  const passing: AcquiredSignal[] = [];
  const rejected: Array<AcquiredSignal & { reasons: string[] }> = [];

  for (const signal of params.signals) {
    const decision = evaluateFilter(signal.issue, config);

    await params.store.recordEvidence({
      executionId: null,
      signalId: signal.signalId,
      source: "deterministic_filter",
      observation: { reasons: decision.reasons, config },
      proves: decision.passes ? "issue passed deterministic filter" : null,
      doesNotProve: decision.passes ? null : `issue rejected: ${decision.reasons.join("; ")}`,
    });

    if (decision.passes) {
      passing.push(signal);
    } else {
      rejected.push({ ...signal, reasons: decision.reasons });
    }
  }

  return { passing, rejected };
}
