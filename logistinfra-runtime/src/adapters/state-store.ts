import type {
  ApprovalInput,
  ApprovalRecord,
  EvidenceInput,
  EvidenceRecord,
  ExecutionInput,
  ExecutionRecord,
  OpportunityInput,
  OpportunityRecord,
  SignalInput,
  SignalRecord,
  UpsertResult,
} from "../types.js";

export interface StateStore {
  upsertSignal(input: SignalInput): Promise<UpsertResult>;
  upsertOpportunity(input: OpportunityInput): Promise<UpsertResult>;
  recordEvidence(input: EvidenceInput): Promise<EvidenceRecord>;
  createExecution(input: ExecutionInput): Promise<ExecutionRecord>;
  updateExecutionStatus(executionId: string, status: string): Promise<void>;
  getExecutionForOpportunity(opportunityId: string): Promise<ExecutionRecord | null>;
  getExecution(executionId: string): Promise<ExecutionRecord | null>;
  recordApproval(input: ApprovalInput): Promise<ApprovalRecord>;
  getLatestApproval(executionId: string): Promise<ApprovalRecord | null>;
  getOpportunity(opportunityId: string): Promise<OpportunityRecord | null>;
  getSignal(signalId: string): Promise<SignalRecord | null>;
}

function randomId(): string {
  return typeof crypto.randomUUID === "function" ? crypto.randomUUID() : Math.random().toString(36).slice(2);
}

export class InMemoryStateStore implements StateStore {
  private signals = new Map<string, SignalRecord>();
  private signalsBySourceKey = new Map<string, string>();
  private opportunities = new Map<string, OpportunityRecord>();
  private opportunitiesBySignalId = new Map<string, string>();
  private evidence = new Map<string, EvidenceRecord>();
  private executions = new Map<string, ExecutionRecord>();
  private executionsByOpportunityId = new Map<string, string>();
  private approvals = new Map<string, ApprovalRecord>();
  private approvalsByExecutionId = new Map<string, string[]>();

  async upsertSignal(input: SignalInput): Promise<UpsertResult> {
    const key = `${input.source}::${input.sourceId}`;
    const existingId = this.signalsBySourceKey.get(key);
    if (existingId) {
      const existing = this.signals.get(existingId)!;
      this.signals.set(existingId, { ...existing, observation: input.observation, sourceUrl: input.sourceUrl });
      return { id: existingId, inserted: false };
    }
    const id = randomId();
    this.signals.set(id, { id, ...input });
    this.signalsBySourceKey.set(key, id);
    return { id, inserted: true };
  }

  async upsertOpportunity(input: OpportunityInput): Promise<UpsertResult> {
    const existingId = this.opportunitiesBySignalId.get(input.signalId);
    if (existingId) {
      const existing = this.opportunities.get(existingId)!;
      this.opportunities.set(existingId, { ...existing, ...input });
      return { id: existingId, inserted: false };
    }
    const id = randomId();
    this.opportunities.set(id, { id, status: "proposed", ...input });
    this.opportunitiesBySignalId.set(input.signalId, id);
    return { id, inserted: true };
  }

  async recordEvidence(input: EvidenceInput): Promise<EvidenceRecord> {
    const id = randomId();
    const record = { id, ...input };
    this.evidence.set(id, record);
    return record;
  }

  async createExecution(input: ExecutionInput): Promise<ExecutionRecord> {
    const id = randomId();
    const record = { id, ...input };
    this.executions.set(id, record);
    this.executionsByOpportunityId.set(input.opportunityId, id);
    return record;
  }

  async updateExecutionStatus(executionId: string, status: string): Promise<void> {
    const existing = this.executions.get(executionId);
    if (!existing) throw new Error(`unknown execution ${executionId}`);
    this.executions.set(executionId, { ...existing, status });
  }

  async getExecutionForOpportunity(opportunityId: string): Promise<ExecutionRecord | null> {
    const id = this.executionsByOpportunityId.get(opportunityId);
    return id ? (this.executions.get(id) ?? null) : null;
  }

  async getExecution(executionId: string): Promise<ExecutionRecord | null> {
    return this.executions.get(executionId) ?? null;
  }

  async recordApproval(input: ApprovalInput): Promise<ApprovalRecord> {
    const id = randomId();
    const record: ApprovalRecord = { id, decidedAt: new Date(), ...input };
    this.approvals.set(id, record);
    const list = this.approvalsByExecutionId.get(input.executionId) ?? [];
    list.push(id);
    this.approvalsByExecutionId.set(input.executionId, list);
    return record;
  }

  async getLatestApproval(executionId: string): Promise<ApprovalRecord | null> {
    const ids = this.approvalsByExecutionId.get(executionId);
    if (!ids || ids.length === 0) return null;
    const last = ids[ids.length - 1]!;
    return this.approvals.get(last) ?? null;
  }

  async getOpportunity(opportunityId: string): Promise<OpportunityRecord | null> {
    return this.opportunities.get(opportunityId) ?? null;
  }

  async getSignal(signalId: string): Promise<SignalRecord | null> {
    return this.signals.get(signalId) ?? null;
  }

  // Test/introspection helpers -- not part of the StateStore contract, but
  // useful for asserting reconstructability without a live Postgres.
  listEvidence(): EvidenceRecord[] {
    return [...this.evidence.values()];
  }

  listExecutions(): ExecutionRecord[] {
    return [...this.executions.values()];
  }

  listOpportunities(): OpportunityRecord[] {
    return [...this.opportunities.values()];
  }

  listSignals(): SignalRecord[] {
    return [...this.signals.values()];
  }
}
