import type { ContextPacket, Receipt } from "../continuity/types.js";

export type AuthorityLevel = "read" | "reversible_write" | "consequential_write" | "human_only";
export type CycleStatus = "idle" | "awaiting_approval" | "executed_unverified" | "settled" | "failed" | "blocked";

export interface ToolCallRequest {
  toolRef: string;
  action: string;
  context: ContextPacket;
}

export interface ToolCallResult {
  ok: boolean;
  raw: Record<string, unknown>;
  externalRef?: string | null;
  error?: string | null;
}

export interface VerificationResult {
  verified: boolean;
  observation: Record<string, unknown>;
  proves?: string | null;
  doesNotProve?: string | null;
}

export interface ToolAdapter {
  ref: string;
  authority: AuthorityLevel;
  execute(request: ToolCallRequest): Promise<ToolCallResult>;
  verify(request: ToolCallRequest, execution: ToolCallResult): Promise<VerificationResult>;
}

export interface ApprovalState {
  approvedTransitionIds: Set<string>;
}

export interface AutonomousCycleResult {
  status: CycleStatus;
  context: ContextPacket | null;
  toolRef?: string | null;
  execution?: ToolCallResult | null;
  verification?: VerificationResult | null;
  receipt?: Receipt | null;
  reason?: string | null;
}
