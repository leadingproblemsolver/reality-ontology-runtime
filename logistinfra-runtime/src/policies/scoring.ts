import type { OpportunityScore } from "../types.js";

const SETUP_BURDEN_SCORE: Record<OpportunityScore["setupBurden"], number> = {
  low: 1,
  medium: 0.5,
  high: 0,
};

const WEIGHTS = {
  reproducibility: 0.3,
  boundedScope: 0.2,
  reliability: 0.2,
  python: 0.1,
  maintainerVerifiable: 0.1,
  setupBurden: 0.1,
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/**
 * Composite score in [0, 1]. Confidence dampens the whole score so a
 * low-confidence read of an otherwise "perfect" issue does not outrank a
 * well-understood, merely-good one.
 */
export function computeCompositeScore(score: OpportunityScore): number {
  const reproducibility = clamp(1 - score.reproducibilityMinutes / 60, 0, 1);
  const python = clamp(score.pythonRelevance / 10, 0, 1);
  const reliability = clamp(score.reliabilityRelevance / 10, 0, 1);
  const setupBurden = SETUP_BURDEN_SCORE[score.setupBurden];

  const raw =
    WEIGHTS.reproducibility * reproducibility +
    WEIGHTS.boundedScope * (score.boundedScope ? 1 : 0) +
    WEIGHTS.reliability * reliability +
    WEIGHTS.python * python +
    WEIGHTS.maintainerVerifiable * (score.maintainerVerifiable ? 1 : 0) +
    WEIGHTS.setupBurden * setupBurden;

  const composite = raw * clamp(score.confidence, 0, 1);
  return Math.round(composite * 10_000) / 10_000;
}
