import { describe, expect, it } from "vitest";
import { DEFAULT_FILTER_CONFIG, evaluateFilter } from "../src/policies/filtering.js";
import type { NormalizedIssue } from "../src/types.js";

function issue(overrides: Partial<NormalizedIssue> = {}): NormalizedIssue {
  return {
    sourceId: "browser-use/browser-use#1",
    owner: "browser-use",
    repo: "browser-use",
    number: 1,
    title: "Something breaks",
    body: "A".repeat(50),
    url: "https://github.com/browser-use/browser-use/issues/1",
    state: "open",
    labels: ["bug"],
    authorLogin: "someone",
    commentsCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

describe("evaluateFilter", () => {
  it("passes a well-formed, recently-updated, open bug report", () => {
    const decision = evaluateFilter(issue());
    expect(decision.passes).toBe(true);
    expect(decision.reasons).toEqual([]);
  });

  it("rejects closed issues", () => {
    const decision = evaluateFilter(issue({ state: "closed" }));
    expect(decision.passes).toBe(false);
    expect(decision.reasons.some((r) => r.includes("not open"))).toBe(true);
  });

  it("rejects issues with a body too short to indicate reproducibility", () => {
    const decision = evaluateFilter(issue({ body: "help" }));
    expect(decision.passes).toBe(false);
    expect(decision.reasons.some((r) => r.includes("too short"))).toBe(true);
  });

  it("rejects issues carrying an excluded label", () => {
    const decision = evaluateFilter(issue({ labels: ["enhancement"] }));
    expect(decision.passes).toBe(false);
    expect(decision.reasons.some((r) => r.includes("excluded label"))).toBe(true);
  });

  it("rejects stale issues past the configured age limit", () => {
    const oldDate = new Date(Date.now() - (DEFAULT_FILTER_CONFIG.maxAgeDaysSinceUpdate + 10) * 86_400_000).toISOString();
    const decision = evaluateFilter(issue({ updatedAt: oldDate }));
    expect(decision.passes).toBe(false);
    expect(decision.reasons.some((r) => r.includes("stale"))).toBe(true);
  });

  it("can report multiple independent rejection reasons at once", () => {
    const decision = evaluateFilter(issue({ state: "closed", body: "x", labels: ["wontfix"] }));
    expect(decision.passes).toBe(false);
    expect(decision.reasons.length).toBeGreaterThanOrEqual(3);
  });
});
