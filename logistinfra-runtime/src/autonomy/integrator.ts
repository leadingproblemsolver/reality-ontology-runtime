import type {
  CapabilityDescriptor,
  IntegrationPlan,
  IntegrationStep,
  OutcomeContract,
} from "./capabilities.js";

function rankCapability(a: CapabilityDescriptor, b: CapabilityDescriptor): number {
  const cost = (a.costRank ?? 100) - (b.costRank ?? 100);
  if (cost !== 0) return cost;
  const quality = (b.qualityRank ?? 0) - (a.qualityRank ?? 0);
  if (quality !== 0) return quality;
  return a.id.localeCompare(b.id);
}

function applicableToLocality(capability: CapabilityDescriptor, locality?: string | null): boolean {
  if (!capability.localities || capability.localities.length === 0) return true;
  if (!locality) return capability.localities.includes("*");
  return capability.localities.includes("*") || capability.localities.includes(locality);
}

function stepFrom(capability: CapabilityDescriptor): IntegrationStep {
  return {
    capabilityId: capability.id,
    kind: capability.kind,
    consumes: capability.requires,
    produces: capability.provides,
    toolRefs: capability.toolRefs,
    authority: capability.authority,
    humanOnly: capability.humanOnly ?? capability.authority === "human_only",
  };
}

/**
 * Deterministic, reuse-first outcome integrator.
 *
 * It performs backwards requirement resolution over a registry of capabilities.
 * It does not execute tools and it does not invent missing capabilities.
 * If the registry cannot satisfy a requirement, that requirement remains explicit.
 */
export function integrateOutcome(
  contract: OutcomeContract,
  registry: CapabilityDescriptor[],
): IntegrationPlan {
  const available = new Set(contract.currentFacts);
  const selected = new Map<string, CapabilityDescriptor>();
  const unresolved = new Set<string>();
  const visiting = new Set<string>();

  const byProvided = new Map<string, CapabilityDescriptor[]>();
  for (const capability of registry) {
    if (!applicableToLocality(capability, contract.locality)) continue;
    for (const provided of capability.provides) {
      const list = byProvided.get(provided) ?? [];
      list.push(capability);
      byProvided.set(provided, list);
    }
  }
  for (const list of byProvided.values()) list.sort(rankCapability);

  function satisfy(requirement: string): boolean {
    if (available.has(requirement)) return true;
    if (visiting.has(requirement)) {
      unresolved.add(requirement);
      return false;
    }

    visiting.add(requirement);
    const candidates = byProvided.get(requirement) ?? [];
    const candidate = candidates.find((capability) =>
      capability.requires.every((dep) => {
        if (available.has(dep)) return true;
        const depCandidates = byProvided.get(dep) ?? [];
        return depCandidates.length > 0;
      }),
    ) ?? candidates[0];

    if (!candidate) {
      unresolved.add(requirement);
      visiting.delete(requirement);
      return false;
    }

    let dependenciesSatisfied = true;
    for (const dependency of candidate.requires) {
      if (!satisfy(dependency)) dependenciesSatisfied = false;
    }

    if (!dependenciesSatisfied) {
      unresolved.add(requirement);
      visiting.delete(requirement);
      return false;
    }

    selected.set(candidate.id, candidate);
    for (const provided of candidate.provides) available.add(provided);
    visiting.delete(requirement);
    return available.has(requirement);
  }

  for (const outcome of contract.requiredOutcomes) satisfy(outcome);

  const ordered: CapabilityDescriptor[] = [];
  const emitted = new Set<string>();
  const selectedList = [...selected.values()];

  function emit(capability: CapabilityDescriptor): void {
    if (emitted.has(capability.id)) return;
    for (const requirement of capability.requires) {
      const producer = selectedList
        .filter((item) => item.provides.includes(requirement))
        .sort(rankCapability)[0];
      if (producer) emit(producer);
    }
    emitted.add(capability.id);
    ordered.push(capability);
  }

  for (const capability of selectedList) emit(capability);

  const humanGates = ordered
    .filter((capability) => capability.humanOnly || capability.authority === "human_only")
    .map((capability) => capability.id);

  return {
    outcomeId: contract.id,
    objective: contract.objective,
    steps: ordered.map(stepFrom),
    unresolvedRequirements: [...unresolved].sort(),
    humanGates,
    doneWhen: contract.requiredOutcomes.join(" + "),
    requiredReceipt: contract.requiredReceipt,
  };
}
