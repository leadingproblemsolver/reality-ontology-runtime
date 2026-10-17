import { describe, expect, it } from "vitest";
import { createModelWorkerAdapter, type TextWorkerInvoker } from "../src/autonomy/model-worker.js";
import { resolveTool } from "../src/autonomy/resolver.js";
import type { ContextPacket } from "../src/continuity/types.js";
import type { ToolAdapter } from "../src/autonomy/types.js";

function context(selector: string): ContextPacket {
  return {
    mission: "prepare bounded artifact",
    workstreamId: "ws",
    currentTruth: ["state=ready"],
    frozenDecisions: ["tool success is not outcome success"],
    evidenceRefs: ["receipt:prior"],
    operator: "test",
    owner: "runtime",
    chatReference: null,
    toolRefs: [selector],
    artifactRefs: ["repo:test"],
    nextAction: "produce a concise implementation packet",
    doneWhen: "inspectable packet exists",
    requiredReceipt: "artifact content hash",
    interruptionWakeCondition: "none",
    transitionId: "t1",
  };
}

function invoker(id: string, model: string, text: string): TextWorkerInvoker {
  return {
    id,
    model,
    async invoke() {
      return { text, raw: { mocked: true }, providerRequestId: `${id}-1` };
    },
  };
}

describe("provider-independent model workers", () => {
  it("produces an inspectable artifact without claiming external consequence", async () => {
    const adapter = createModelWorkerAdapter({
      ref: "tool:test-worker",
      invoker: invoker("provider-a", "model-a", "bounded result"),
      capabilities: ["artifact.compile"],
      costRank: 10,
      qualityRank: 80,
    });

    const request = {
      toolRef: adapter.ref,
      action: context("cap:artifact.compile").nextAction,
      context: context("cap:artifact.compile"),
    };

    const execution = await adapter.execute(request);
    const verification = await adapter.verify(request, execution);

    expect(execution.ok).toBe(true);
    expect(verification.verified).toBe(true);
    expect(verification.proves).toContain("inspectable worker artifact");
    expect(verification.doesNotProve).toContain("external state change");
  });

  it("allows the same capability to move between providers without changing transition schema", () => {
    const cheap = createModelWorkerAdapter({
      ref: "tool:cheap",
      invoker: invoker("cheap-provider", "cheap-model", "x"),
      capabilities: ["research.synthesize"],
      costRank: 5,
      qualityRank: 70,
    });
    const premium = createModelWorkerAdapter({
      ref: "tool:premium",
      invoker: invoker("premium-provider", "premium-model", "x"),
      capabilities: ["research.synthesize"],
      costRank: 40,
      qualityRank: 100,
    });

    const tools = new Map<string, ToolAdapter>([
      [cheap.ref, cheap],
      [premium.ref, premium],
    ]);
    const resolved = resolveTool(context("cap:research.synthesize"), tools);

    expect(resolved?.toolRef).toBe("tool:cheap");
  });

  it("refuses empty worker output", async () => {
    const adapter = createModelWorkerAdapter({
      ref: "tool:empty",
      invoker: invoker("provider", "model", "   "),
      capabilities: ["artifact.compile"],
    });
    const request = {
      toolRef: adapter.ref,
      action: "produce artifact",
      context: context("cap:artifact.compile"),
    };

    const execution = await adapter.execute(request);
    expect(execution.ok).toBe(false);
    expect(execution.error).toContain("empty output");
  });
});
