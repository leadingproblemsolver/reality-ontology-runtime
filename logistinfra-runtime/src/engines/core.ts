import type { CapabilityDescriptor, IntegrationPlan, OutcomeContract } from "../autonomy/capabilities.js";
import { integrateOutcome } from "../autonomy/integrator.js";

export type PriorityBand = "P-1" | "P0" | "P1" | "P2" | "P3";
export type EngineDisposition = "EXECUTE" | "WATCH" | "BLOCKED" | "KILL" | "VERIFY" | "PACKAGE";

export interface MarketCandidate {
  id: string;
  priority: PriorityBand;
  state: string;
  nextAction: string;
  externalConsequence?: boolean;
  waitingExternal?: boolean;
  wakeConditionMet?: boolean;
  authorityAvailable?: boolean;
  receiptRequired?: string;
}

export interface MarketDecision {
  disposition: EngineDisposition;
  candidate: MarketCandidate | null;
  reason: string;
  doneWhen: string | null;
}

const PRIORITY: Record<PriorityBand, number> = {
  "P-1": 500,
  "P0": 400,
  "P1": 300,
  "P2": 200,
  "P3": 100,
};

export function routeMarket(candidates: MarketCandidate[]): MarketDecision {
  const executable = candidates
    .filter((candidate) => candidate.state !== "KILL")
    .filter((candidate) => !(candidate.waitingExternal && !candidate.wakeConditionMet))
    .filter((candidate) => candidate.authorityAvailable !== false)
    .sort((a, b) => {
      const consequence = Number(Boolean(b.externalConsequence)) - Number(Boolean(a.externalConsequence));
      if (consequence !== 0) return consequence;
      return PRIORITY[b.priority] - PRIORITY[a.priority] || a.id.localeCompare(b.id);
    });

  const selected = executable[0] ?? null;
  if (selected) {
    return {
      disposition: "EXECUTE",
      candidate: selected,
      reason: "highest-consequence dependency-correct transition with authority available",
      doneWhen: selected.receiptRequired ?? "fresh external state proves the requested transition",
    };
  }

  const blocked = candidates.find((candidate) => candidate.authorityAvailable === false);
  if (blocked) {
    return {
      disposition: "BLOCKED",
      candidate: blocked,
      reason: "required authority is unavailable; preparation may continue but no consequential write is admissible",
      doneWhen: blocked.receiptRequired ?? null,
    };
  }

  const waiting = candidates.find((candidate) => candidate.waitingExternal && !candidate.wakeConditionMet);
  if (waiting) {
    return {
      disposition: "WATCH",
      candidate: waiting,
      reason: "waiting work is suppressed until its wake condition fires",
      doneWhen: waiting.receiptRequired ?? null,
    };
  }

  return { disposition: "KILL", candidate: null, reason: "no admissible market transition", doneWhen: null };
}

export type EvidenceState =
  | "historical_unchecked"
  | "source_inspected"
  | "fixture_inspected"
  | "locally_tested"
  | "ci_documented"
  | "ci_live_verified"
  | "externally_reviewed"
  | "used_in_real_workflow"
  | "paid";

const EVIDENCE_RANK: Record<EvidenceState, number> = {
  historical_unchecked: 0,
  source_inspected: 1,
  fixture_inspected: 2,
  locally_tested: 3,
  ci_documented: 3,
  ci_live_verified: 4,
  externally_reviewed: 5,
  used_in_real_workflow: 6,
  paid: 7,
};

export interface ProofDecision {
  current: EvidenceState;
  required: EvidenceState;
  passes: boolean;
  disposition: "PACKAGE" | "VERIFY";
  missingGate: string | null;
}

export function routeProof(current: EvidenceState, required: EvidenceState): ProofDecision {
  const passes = EVIDENCE_RANK[current] >= EVIDENCE_RANK[required];
  return {
    current,
    required,
    passes,
    disposition: passes ? "PACKAGE" : "VERIFY",
    missingGate: passes ? null : `evidence must advance from ${current} to at least ${required}`,
  };
}

export function routeOutcome(contract: OutcomeContract, registry: CapabilityDescriptor[]): IntegrationPlan {
  return integrateOutcome(contract, registry);
}
