import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { StateStore } from "./state-store.js";
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

export class SupabaseStateStore implements StateStore {
  private client: SupabaseClient;

  constructor(url: string, serviceRoleKey: string) {
    this.client = createClient(url, serviceRoleKey, { auth: { persistSession: false } });
  }

  async upsertSignal(input: SignalInput): Promise<UpsertResult> {
    const { data: existing, error: selectError } = await this.client
      .from("signals")
      .select("id")
      .eq("source", input.source)
      .eq("source_id", input.sourceId)
      .maybeSingle();
    if (selectError) throw new Error(`supabase select signals failed: ${selectError.message}`);

    if (existing) {
      const { error: updateError } = await this.client
        .from("signals")
        .update({ source_url: input.sourceUrl, observation: input.observation })
        .eq("id", existing.id);
      if (updateError) throw new Error(`supabase update signals failed: ${updateError.message}`);
      return { id: existing.id, inserted: false };
    }

    const { data: inserted, error: insertError } = await this.client
      .from("signals")
      .insert({
        source: input.source,
        source_id: input.sourceId,
        source_url: input.sourceUrl,
        observation: input.observation,
      })
      .select("id")
      .single();
    if (insertError) throw new Error(`supabase insert signals failed: ${insertError.message}`);
    return { id: inserted.id, inserted: true };
  }

  async upsertOpportunity(input: OpportunityInput): Promise<UpsertResult> {
    const { data: existing, error: selectError } = await this.client
      .from("opportunities")
      .select("id")
      .eq("signal_id", input.signalId)
      .maybeSingle();
    if (selectError) throw new Error(`supabase select opportunities failed: ${selectError.message}`);

    const row = {
      signal_id: input.signalId,
      target: input.target,
      problem: input.problem,
      score: input.score,
      rationale: input.rationale,
      uncertainty: input.uncertainty,
      recommended_action: input.recommendedAction,
    };

    if (existing) {
      const { error: updateError } = await this.client.from("opportunities").update(row).eq("id", existing.id);
      if (updateError) throw new Error(`supabase update opportunities failed: ${updateError.message}`);
      return { id: existing.id, inserted: false };
    }

    const { data: inserted, error: insertError } = await this.client
      .from("opportunities")
      .insert(row)
      .select("id")
      .single();
    if (insertError) throw new Error(`supabase insert opportunities failed: ${insertError.message}`);
    return { id: inserted.id, inserted: true };
  }

  async recordEvidence(input: EvidenceInput): Promise<EvidenceRecord> {
    const { data, error } = await this.client
      .from("evidence")
      .insert({
        execution_id: input.executionId,
        signal_id: input.signalId,
        source: input.source,
        observation: input.observation,
        proves: input.proves,
        does_not_prove: input.doesNotProve,
      })
      .select("id")
      .single();
    if (error) throw new Error(`supabase insert evidence failed: ${error.message}`);
    return { id: data.id, ...input };
  }

  async createExecution(input: ExecutionInput): Promise<ExecutionRecord> {
    const { data, error } = await this.client
      .from("executions")
      .insert({
        opportunity_id: input.opportunityId,
        action: input.action,
        expected_transition: input.expectedTransition,
        approval_required: input.approvalRequired,
        status: input.status,
      })
      .select("id")
      .single();
    if (error) throw new Error(`supabase insert executions failed: ${error.message}`);
    return { id: data.id, ...input };
  }

  async updateExecutionStatus(executionId: string, status: string): Promise<void> {
    const { error } = await this.client.from("executions").update({ status }).eq("id", executionId);
    if (error) throw new Error(`supabase update executions failed: ${error.message}`);
  }

  async getExecutionForOpportunity(opportunityId: string): Promise<ExecutionRecord | null> {
    const { data, error } = await this.client
      .from("executions")
      .select("*")
      .eq("opportunity_id", opportunityId)
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle();
    if (error) throw new Error(`supabase select executions failed: ${error.message}`);
    return data ? mapExecutionRow(data) : null;
  }

  async getExecution(executionId: string): Promise<ExecutionRecord | null> {
    const { data, error } = await this.client.from("executions").select("*").eq("id", executionId).maybeSingle();
    if (error) throw new Error(`supabase select executions failed: ${error.message}`);
    return data ? mapExecutionRow(data) : null;
  }

  async recordApproval(input: ApprovalInput): Promise<ApprovalRecord> {
    const { data, error } = await this.client
      .from("approvals")
      .insert({
        execution_id: input.executionId,
        decision: input.decision,
        payload_hash: input.payloadHash ?? null,
      })
      .select("id, decided_at")
      .single();
    if (error) throw new Error(`supabase insert approvals failed: ${error.message}`);
    return { id: data.id, decidedAt: new Date(data.decided_at), ...input };
  }

  async getLatestApproval(executionId: string): Promise<ApprovalRecord | null> {
    const { data, error } = await this.client
      .from("approvals")
      .select("*")
      .eq("execution_id", executionId)
      .order("decided_at", { ascending: false })
      .limit(1)
      .maybeSingle();
    if (error) throw new Error(`supabase select approvals failed: ${error.message}`);
    if (!data) return null;
    return {
      id: data.id,
      executionId: data.execution_id,
      decision: data.decision,
      payloadHash: data.payload_hash,
      decidedAt: new Date(data.decided_at),
    };
  }

  async getOpportunity(opportunityId: string): Promise<OpportunityRecord | null> {
    const { data, error } = await this.client.from("opportunities").select("*").eq("id", opportunityId).maybeSingle();
    if (error) throw new Error(`supabase select opportunities failed: ${error.message}`);
    if (!data) return null;
    return {
      id: data.id,
      signalId: data.signal_id,
      target: data.target,
      problem: data.problem,
      score: data.score,
      rationale: data.rationale,
      uncertainty: data.uncertainty,
      recommendedAction: data.recommended_action,
      status: data.status,
    };
  }

  async getSignal(signalId: string): Promise<SignalRecord | null> {
    const { data, error } = await this.client.from("signals").select("*").eq("id", signalId).maybeSingle();
    if (error) throw new Error(`supabase select signals failed: ${error.message}`);
    if (!data) return null;
    return {
      id: data.id,
      source: data.source,
      sourceId: data.source_id,
      sourceUrl: data.source_url,
      observation: data.observation,
    };
  }
}

function mapExecutionRow(data: Record<string, unknown>): ExecutionRecord {
  return {
    id: data.id as string,
    opportunityId: data.opportunity_id as string,
    action: data.action as string,
    expectedTransition: data.expected_transition as string | null,
    approvalRequired: data.approval_required as boolean,
    status: data.status as string,
  };
}
