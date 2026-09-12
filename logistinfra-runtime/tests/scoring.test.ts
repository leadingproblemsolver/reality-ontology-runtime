import { describe, expect, it } from "vitest";
import { computeCompositeScore } from "../src/policies/scoring.js";
import type { OpportunityScore } from "../src/types.js";

function score(overrides: Partial<OpportunityScore> = {}): OpportunityScore {
  return {
    reproducibilityMinutes: 30,
    boundedScope: true,
    pythonRelevance: 10,
    reliabilityRelevance: 10,
    maintainerVerifiable: true,
    setupBurden: "low",
    confidence: 1,
    rationale: "r",
    uncertainty: "u",
    expectedInvariant: "i",
    reproductionHypothesis: "h",
    suggestedFirstTest: "t",
    filesToInspect: [],
    recommendedAction: "investigate",
    ...overrides,
  };
}

describe("computeCompositeScore", () => {
  it("scores a best-case issue near the maximum of 1", () => {
    const composite = computeCompositeScore(score({ reproducibilityMinutes: 0 }));
    expect(composite).toBeGreaterThan(0.9);
    expect(composite).toBeLessThanOrEqual(1);
  });

  it("zeroes out the reproducibility term once estimated time exceeds 60 minutes", () => {
    const fast = computeCompositeScore(score({ reproducibilityMinutes: 10 }));
    const slow = computeCompositeScore(score({ reproducibilityMinutes: 90 }));
    expect(slow).toBeLessThan(fast);
  });

  it("dampens the whole score by confidence", () => {
    const confident = computeCompositeScore(score({ confidence: 1 }));
    const unsure = computeCompositeScore(score({ confidence: 0.2 }));
    expect(unsure).toBeCloseTo(confident * 0.2, 4);
  });

  it("returns 0 for zero confidence regardless of other fields", () => {
    expect(computeCompositeScore(score({ confidence: 0 }))).toBe(0);
  });

  it("rewards low setup burden over high setup burden, all else equal", () => {
    const low = computeCompositeScore(score({ setupBurden: "low" }));
    const high = computeCompositeScore(score({ setupBurden: "high" }));
    expect(low).toBeGreaterThan(high);
  });
});
