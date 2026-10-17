import type { AuthorityLevel } from "./types.js";

export type CapabilityKind =
  | "sense"
  | "structuralize"
  | "map"
  | "evaluate"
  | "decide"
  | "prioritize"
  | "plan"
  | "execute"
  | "verify"
  | "ship"
  | "externalize"
  | "market"
  | "close"
  | "maintain"
  | "embed"
  | "scale"
  | "integrate";

export interface CapabilityDescriptor {
  id: string;
  kind: CapabilityKind;
  description: string;
  requires: string[];
  provides: string[];
  toolRefs: string[];
  authority: AuthorityLevel;
  costRank?: number;
  qualityRank?: number;
  humanOnly?: boolean;
  localities?: string[];
}

export interface OutcomeContract {
  id: string;
  objective: string;
  currentFacts: string[];
  requiredOutcomes: string[];
  requiredReceipt: string;
  constraints: string[];
  authority: AuthorityLevel;
  locality?: string | null;
}

export interface IntegrationStep {
  capabilityId: string;
  kind: CapabilityKind;
  consumes: string[];
  produces: string[];
  toolRefs: string[];
  authority: AuthorityLevel;
  humanOnly: boolean;
}

export interface IntegrationPlan {
  outcomeId: string;
  objective: string;
  steps: IntegrationStep[];
  unresolvedRequirements: string[];
  humanGates: string[];
  doneWhen: string;
  requiredReceipt: string;
}
