import { describe, expect, it } from "vitest";
import { integrateOutcome } from "../src/autonomy/integrator.js";
import type { CapabilityDescriptor, OutcomeContract } from "../src/autonomy/capabilities.js";

const registry: CapabilityDescriptor[] = [
  {
    id: "structuralizer",
    kind: "structuralize",
    description: "turn raw input into a bounded task contract",
    requires: ["raw_input"],
    provides: ["structured_task"],
    toolRefs: ["cap:reason.complex"],
    authority: "read",
    costRank: 5,
  },
  {
    id: "mapper",
    kind: "map",
    description: "map a structured task to existing tools and assets",
    requires: ["structured_task"],
    provides: ["reuse_map"],
    toolRefs: ["cap:research.synthesize"],
    authority: "read",
    costRank: 5,
  },
  {
    id: "executor",
    kind: "execute",
    description: "execute the selected bounded action",
    requires: ["reuse_map"],
    provides: ["external_effect_attempted"],
    toolRefs: ["cap:cross_app.orchestrate"],
    authority: "reversible_write",
    costRank: 20,
  },
  {
    id: "verifier",
    kind: "verify",
    description: "freshly reread the external system",
    requires: ["external_effect_attempted"],
    provides: ["verified_external_state"],
    toolRefs: ["cap:verification.review"],
    authority: "read",
    costRank: 10,
  },
  {
    id: "human-closer",
    kind: "close",
    description: "human negotiation/commitment",
    requires: ["qualified_conversation"],
    provides: ["commercial_commitment"],
    toolRefs: [],
    authority: "human_only",
    humanOnly: true,
    costRank: 100,
  },
];

function contract(requiredOutcomes: string[], currentFacts = ["raw_input"]): OutcomeContract {
  return {
    id: "outcome-1",
    objective: "achieve a verified external result",
    currentFacts,
    requiredOutcomes,
    requiredReceipt: "independently readable external state",
    constraints: [],
    authority: "reversible_write",
    locality: "Doha",
  };
}

describe("outcome integrator", () => {
  it("composes the minimum dependency chain from raw input to verified state", () => {
    const plan = integrateOutcome(contract(["verified_external_state"]), registry);
    expect(plan.unresolvedRequirements).toEqual([]);
    expect(plan.steps.map((step) => step.capabilityId)).toEqual([
      "structuralizer",
      "mapper",
      "executor",
      "verifier",
    ]);
    expect(plan.humanGates).toEqual([]);
  });

  it("does not invent capabilities when the required outcome is missing", () => {
    const plan = integrateOutcome(contract(["paid_invoice"]), registry);
    expect(plan.steps).toEqual([]);
    expect(plan.unresolvedRequirements).toEqual(["paid_invoice"]);
  });

  it("surfaces irreducible human gates explicitly", () => {
    const plan = integrateOutcome(
      contract(["commercial_commitment"], ["qualified_conversation"]),
      registry,
    );
    expect(plan.unresolvedRequirements).toEqual([]);
    expect(plan.humanGates).toEqual(["human-closer"]);
    expect(plan.steps[0]?.kind).toBe("close");
  });
});
