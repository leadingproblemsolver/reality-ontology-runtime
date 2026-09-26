import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { JsonContinuityStore } from "../src/continuity/store.js";
import { runAutonomousCycle, runUntilBoundary } from "../src/autonomy/engine.js";
import type { GlobalState } from "../src/continuity/types.js";
import type { ToolAdapter } from "../src/autonomy/types.js";

function baseState(authorityTool = "tool:read"): GlobalState {
  return {
    version: 1,
    updatedAt: "2026-09-20T00:00:00.000Z",
    goals: ["produce external proof"],
    frozenDecisions: ["tool success is not outcome success"],
    chats: [{
      id: "operator-chat",
      title: "Operator",
      purpose: "execute bounded transition",
      operator: "test_operator",
      workstreamId: "ws",
      invokeWhen: ["transition eligible"],
      artifacts: [],
      latestState: "ready",
      sourceRefs: ["fixture"],
    }],
    workstreams: [{
      id: "ws",
      objective: "advance safely",
      status: "active",
      currentState: "s0",
      priority: 100,
      operator: "test_operator",
      chatId: "operator-chat",
      artifactRefs: [],
    }],
    transitions: [
      {
        id: "t1",
        workstreamId: "ws",
        mission: "advance",
        fromState: "s0",
        toState: "s1",
        action: "perform first action",
        operator: "test_operator",
        owner: "agent",
        status: "pending",
        priority: 100,
        receiptRequired: "verified state change",
        doneWhen: "s1 observed",
        interruptionWakeCondition: "urgent external event",
        chatId: "operator-chat",
        artifactRefs: [],
        toolRefs: [authorityTool],
        evidenceRefs: [],
        dependsOn: [],
        createdAt: "2026-09-20T00:00:00.000Z",
      },
      {
        id: "t2",
        workstreamId: "ws",
        mission: "advance",
        fromState: "s1",
        toState: "s2",
        action: "perform second action",
        operator: "test_operator",
        owner: "agent",
        status: "pending",
        priority: 90,
        receiptRequired: "verified state change",
        doneWhen: "s2 observed",
        interruptionWakeCondition: "urgent external event",
        chatId: "operator-chat",
        artifactRefs: [],
        toolRefs: ["tool:read"],
        evidenceRefs: [],
        dependsOn: ["t1"],
        createdAt: "2026-09-20T00:01:00.000Z",
      },
    ],
    receipts: [],
  };
}

async function makeStore(state: GlobalState): Promise<JsonContinuityStore> {
  const dir = await mkdtemp(join(tmpdir(), "logistinfra-autonomy-"));
  const path = join(dir, "state.json");
  await writeFile(path, JSON.stringify(state, null, 2));
  return new JsonContinuityStore(path);
}

function verifiedTool(ref = "tool:read", authority: ToolAdapter["authority"] = "read"): ToolAdapter {
  return {
    ref,
    authority,
    async execute() {
      return { ok: true, raw: { tool_status: "success" }, externalRef: "ext-1" };
    },
    async verify(_request, execution) {
      return {
        verified: true,
        observation: { externalRef: execution.externalRef, observed_state: "changed" },
        proves: "expected state transition observed",
        doesNotProve: "future durability",
      };
    },
  };
}

describe("autonomous runtime kernel", () => {
  it("executes, verifies, settles, and advances through multiple transitions", async () => {
    const store = await makeStore(baseState());
    const tools = new Map<string, ToolAdapter>([["tool:read", verifiedTool()]]);
    const results = await runUntilBoundary({
      store,
      mission: "advance",
      tools,
      approvals: { approvedTransitionIds: new Set() },
      maxCycles: 5,
      now: () => "2026-09-20T01:00:00.000Z",
    });

    expect(results.map((r) => r.status)).toEqual(["settled", "settled", "idle"]);
    expect(results[0]?.context?.transitionId).toBe("t1");
    expect(results[1]?.context?.transitionId).toBe("t2");
    const state = await store.load();
    expect(state.workstreams[0]?.status).toBe("done");
    expect(state.receipts).toHaveLength(2);
  });

  it("does not execute consequential writes without approval", async () => {
    const store = await makeStore(baseState("tool:write"));
    const tools = new Map<string, ToolAdapter>([
      ["tool:write", verifiedTool("tool:write", "consequential_write")],
      ["tool:read", verifiedTool()],
    ]);

    const result = await runAutonomousCycle({
      store,
      mission: "advance",
      tools,
      approvals: { approvedTransitionIds: new Set() },
    });

    expect(result.status).toBe("awaiting_approval");
    const state = await store.load();
    expect(state.receipts).toHaveLength(0);
    expect(state.transitions.find((t) => t.id === "t1")?.status).toBe("pending");
  });

  it("executes an approved consequential write and settles only after fresh verification", async () => {
    const store = await makeStore(baseState("tool:write"));
    const tools = new Map<string, ToolAdapter>([
      ["tool:write", verifiedTool("tool:write", "consequential_write")],
      ["tool:read", verifiedTool()],
    ]);

    const result = await runAutonomousCycle({
      store,
      mission: "advance",
      tools,
      approvals: { approvedTransitionIds: new Set(["t1"]) },
    });

    expect(result.status).toBe("settled");
    expect(result.receipt?.verified).toBe(true);
  });

  it("never settles merely because a tool reported success", async () => {
    const store = await makeStore(baseState());
    const lyingTool: ToolAdapter = {
      ref: "tool:read",
      authority: "read",
      async execute() {
        return { ok: true, raw: { status: "success" } };
      },
      async verify() {
        return {
          verified: false,
          observation: { observed_state: "unchanged" },
          proves: null,
          doesNotProve: "expected state transition did not occur",
        };
      },
    };

    const result = await runAutonomousCycle({
      store,
      mission: "advance",
      tools: new Map([["tool:read", lyingTool]]),
      approvals: { approvedTransitionIds: new Set() },
    });

    expect(result.status).toBe("executed_unverified");
    const state = await store.load();
    expect(state.receipts).toHaveLength(0);
    expect(state.transitions.find((t) => t.id === "t1")?.status).toBe("pending");
  });
});
