export interface NormalizedIssue {
  sourceId: string;
  owner: string;
  repo: string;
  number: number;
  title: string;
  body: string;
  url: string;
  state: string;
  labels: string[];
  authorLogin: string | null;
  commentsCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface OpportunityScore {
  reproducibilityMinutes: number;
  boundedScope: boolean;
  pythonRelevance: number;
  reliabilityRelevance: number;
  maintainerVerifiable: boolean;
  setupBurden: "low" | "medium" | "high";
  confidence: number;
  rationale: string;
  uncertainty: string;
  expectedInvariant: string;
  reproductionHypothesis: string;
  suggestedFirstTest: string;
  filesToInspect: string[];
  recommendedAction: string;
}

export interface SignalInput {
  source: string;
  sourceId: string;
  sourceUrl: string | null;
  observation: Record<string, unknown>;
  observedAt?: Date;
}

export interface SignalRecord extends SignalInput {
  id: string;
}

export interface OpportunityInput {
  signalId: string;
  target: string | null;
  problem: string | null;
  score: number;
  rationale: Record<string, unknown>;
  uncertainty: string | null;
  recommendedAction: string | null;
}

export interface OpportunityRecord extends OpportunityInput {
  id: string;
  status: string;
}

export interface ExecutionInput {
  opportunityId: string;
  action: string;
  expectedTransition: string | null;
  approvalRequired: boolean;
  status: string;
}

export interface ExecutionRecord extends ExecutionInput {
  id: string;
}

export type ApprovalDecision = "approved" | "rejected";

export interface ApprovalInput {
  executionId: string;
  decision: ApprovalDecision;
  payloadHash?: string | null;
}

export interface ApprovalRecord extends ApprovalInput {
  id: string;
  decidedAt: Date;
}

export interface EvidenceInput {
  executionId: string | null;
  signalId: string | null;
  source: string;
  observation: Record<string, unknown>;
  proves: string | null;
  doesNotProve: string | null;
}

export interface EvidenceRecord extends EvidenceInput {
  id: string;
}

export interface UpsertResult {
  id: string;
  inserted: boolean;
}

export interface InvestigationPacket {
  repo: string;
  issueNumber: number;
  issueUrl: string;
  filesToInspect: string[];
  reproductionHypothesis: string;
  expectedInvariant: string;
  firstTest: string;
}
