import type { ContinuityStore } from "../continuity/store.js";
import { route, settle } from "../continuity/engine.js";
import type { Receipt } from "../continuity/types.js";
import type {
  ApprovalState,
  AutonomousCycleResult,
  ToolAdapter,
  ToolCallRequest,
} from "./types.js";

function needsApproval(authority: ToolAdapter["authority"]): boolean {
  return authority === "consequential_write" || authority === "human_only";
}

function receiptId(transitionId: string): string {
  return `receipt-${transitionId}-${Date.now()}`;
}

export async function runAutonomousCycle(params: {
  store: ContinuityStore;
  mission: string;
  tools: Map<string, ToolAdapter>;
  approvals: ApprovalState;
  now?: () => string;
}): Promise<AutonomousCycleResult> {
  const context = await route(params.store, params.mission);
  if (!context) {
    return { status: "idle", context: null, reason: "no admissible transition" };
  }

  const toolRef = context.toolRefs[0] ?? null;
  if (!toolRef) {
    return {
      status: "blocked",
      context,
      toolRef: null,
      reason: "transition has no executable tool reference",
    };
  }

  const tool = params.tools.get(toolRef);
  if (!tool) {
    return {
      status: "blocked",
      context,
      toolRef,
      reason: `no adapter registered for ${toolRef}`,
    };
  }

  if (tool.authority === "human_only") {
    return {
      status: "awaiting_approval",
      context,
      toolRef,
      reason: "transition requires human execution",
    };
  }

  if (needsApproval(tool.authority) && !params.approvals.approvedTransitionIds.has(context.transitionId)) {
    return {
      status: "awaiting_approval",
      context,
      toolRef,
      reason: "consequential write requires explicit approval",
    };
  }

  const request: ToolCallRequest = {
    toolRef,
    action: context.nextAction,
    context,
  };

  let execution;
  try {
    execution = await tool.execute(request);
  } catch (error) {
    return {
      status: "failed",
      context,
      toolRef,
      reason: error instanceof Error ? error.message : String(error),
    };
  }

  if (!execution.ok) {
    return {
      status: "failed",
      context,
      toolRef,
      execution,
      reason: execution.error ?? "tool execution failed",
    };
  }

  let verification;
  try {
    verification = await tool.verify(request, execution);
  } catch (error) {
    return {
      status: "executed_unverified",
      context,
      toolRef,
      execution,
      reason: `verification failed: ${error instanceof Error ? error.message : String(error)}`,
    };
  }

  if (!verification.verified || !verification.proves) {
    return {
      status: "executed_unverified",
      context,
      toolRef,
      execution,
      verification,
      reason: verification.doesNotProve ?? "expected transition was not independently verified",
    };
  }

  const verifiedAt = params.now ? params.now() : new Date().toISOString();
  const receipt: Receipt = {
    id: receiptId(context.transitionId),
    transitionId: context.transitionId,
    source: toolRef,
    observation: verification.observation,
    proves: verification.proves,
    doesNotProve: verification.doesNotProve ?? null,
    verified: true,
    verifiedAt,
  };

  await settle(params.store, receipt);

  return {
    status: "settled",
    context,
    toolRef,
    execution,
    verification,
    receipt,
  };
}

export async function runUntilBoundary(params: {
  store: ContinuityStore;
  mission: string;
  tools: Map<string, ToolAdapter>;
  approvals: ApprovalState;
  maxCycles?: number;
  now?: () => string;
}): Promise<AutonomousCycleResult[]> {
  const results: AutonomousCycleResult[] = [];
  const maxCycles = params.maxCycles ?? 10;

  for (let i = 0; i < maxCycles; i += 1) {
    const result = await runAutonomousCycle(params);
    results.push(result);
    if (result.status !== "settled") break;
  }

  return results;
}
