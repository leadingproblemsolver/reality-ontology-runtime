import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { JsonContinuityStore } from "../src/continuity/store.js";
import { route, settle, sync } from "../src/continuity/engine.js";
import type { GlobalState, Receipt } from "../src/continuity/types.js";

function seed(): GlobalState {
  return {
    version: 1,
    updatedAt: "2026-09-19T00:00:00.000Z",
    goals: ["convert accumulated work into verified external proof"],
    frozenDecisions: [
      "Market Router owns market-facing prioritization",
      "Reality Ontology owns evidence/current-state truth",
      "Moment Router owns immediate transition selection",
    ],
    chats: [
      {
        id: "market-router",
        title: "Market Router Setup",
        purpose: "select the highest-leverage market-facing transition",
        operator: "market_router",
        workstreamId: "ws-market-proof",
        invokeWhen: ["qualified target exists"],
        artifacts: ["artifact:signalops-workbench"],
        latestState: "target selected",
        sourceRefs: ["chat:market-router"],
      },
      {
        id: "direct-gtm",
        title: "Direct GTM Chats",
        purpose: "execute the approved external market action",
        operator: "direct_gtm",
        workstreamId: "ws-market-proof",
        invokeWhen: ["intervention prepared"],
        artifacts: ["artifact:signalops-workbench"],
        latestState: "ready to send",
        sourceRefs: ["chat:direct-gtm"],
      },
    ],
    workstreams: [
      {
        id: "ws-market-proof",
        objective: "turn an existing technical artifact into an external receipt",
        status: "active",
        currentState: "artifact_selected",
        priority: 100,
        operator: "market_router",
        chatId: "market-router",
        artifactRefs: ["artifact:signalops-workbench"],
      },
      {
        id: "ws-waiting",
        objective: "wait for external reply",
        status: "waiting",
        currentState: "message_sent",
        priority: 999,
        operator: "message_triage",
        artifactRefs: [],
        waitingUntil: "2026-09-20T12:00:00.000Z",
      },
    ],
    transitions: [
      {
        id: "t1",
        workstreamId: "ws-market-proof",
        mission: "obtain external proof",
        fromState: "artifact_selected",
        toState: "intervention_prepared",
        action: "prepare one target-specific intervention from the existing artifact",
        operator: "market_router",
        owner: "Taha",
        status: "pending",
        priority: 100,
        receiptRequired: "verified intervention artifact",
        doneWhen: "intervention is inspectable and tied to one observed target problem",
        interruptionWakeCondition: "new external reply or hard deadline",
        chatId: "market-router",
        artifactRefs: ["artifact:signalops-workbench"],
        evidenceRefs: ["evidence:artifact-exists"],
        dependsOn: [],
        createdAt: "2026-09-19T00:00:00.000Z",
      },
      {
        id: "t2",
        workstreamId: "ws-market-proof",
        mission: "obtain external proof",
        fromState: "intervention_prepared",
        toState: "external_action_sent",
        action: "send the prepared intervention to the selected external target",
        operator: "direct_gtm",
        owner: "Taha",
        status: "pending",
        priority: 100,
        receiptRequired: "send/submission receipt",
        doneWhen: "external system confirms delivery/submission",
        interruptionWakeCondition: "target replies before planned follow-up",
        chatId: "direct-gtm",
        artifactRefs: ["artifact:signalops-workbench"],
        toolRefs: ["tool:gmail"],
        evidenceRefs: [],
        dependsOn: ["t1"],
        createdAt: "2026-09-19T00:01:00.000Z",
      },
    ],
    receipts: [],
  };
}

describe("live context engine", () => {
  it("reconstructs a fresh session and advances instead of repeating a settled transition", async () => {
    const dir = await mkdtemp(join(tmpdir(), "logistinfra-continuity-"));
    const path = join(dir, "state.json");
    await writeFile(path, JSON.stringify(seed(), null, 2));

    // Session A
    const sessionA = new JsonContinuityStore(path);
    const first = await route(sessionA, "obtain external proof");
    expect(first?.transitionId).toBe("t1");
    expect(first?.chatReference).toMatch(/Market Router Setup/);
    expect(first?.artifactRefs).toContain("artifact:signalops-workbench");

    const receipt: Receipt = {
      id: "r1",
      transitionId: "t1",
      source: "fixture_verifier",
      observation: { artifact: "target-specific intervention" },
      proves: "the intervention artifact was produced and inspected",
      doesNotProve: "that an external target received or used it",
      verified: true,
      verifiedAt: "2026-09-19T00:10:00.000Z",
    };
    await settle(sessionA, receipt);

    // Fresh Session B: new process-equivalent store instance; no prior object memory.
    const sessionB = new JsonContinuityStore(path);
    const synced = await sync(sessionB);
    expect(synced.active.map((w) => w.id)).toContain("ws-market-proof");
    expect(synced.waiting.map((w) => w.id)).toContain("ws-waiting");

    const second = await route(sessionB, "obtain external proof");
    expect(second?.transitionId).toBe("t2");
    expect(second?.nextAction).toMatch(/send the prepared intervention/i);
    expect(second?.chatReference).toMatch(/Direct GTM Chats/);
    expect(second?.owner).toBe("Taha");
    expect(second?.toolRefs).toContain("tool:gmail");
    expect(second?.currentTruth.join(" ")).toMatch(/last_verified_transition=t1/);
    expect(second?.currentTruth.join(" ")).toMatch(/intervention artifact was produced/);
    expect(second?.evidenceRefs).toContain("receipt:r1");
  });

  it("does not settle from an unverified receipt", async () => {
    const dir = await mkdtemp(join(tmpdir(), "logistinfra-continuity-"));
    const path = join(dir, "state.json");
    await writeFile(path, JSON.stringify(seed(), null, 2));
    const store = new JsonContinuityStore(path);

    await expect(settle(store, {
      id: "bad",
      transitionId: "t1",
      source: "tool_claim",
      observation: { status: "success" },
      proves: "claimed success",
      verified: false,
      verifiedAt: "2026-09-19T00:10:00.000Z",
    })).rejects.toThrow(/not independently verified/);

    const next = await route(store, "obtain external proof");
    expect(next?.transitionId).toBe("t1");
  });

  it("suppresses waiting work even when its priority is numerically higher", async () => {
    const dir = await mkdtemp(join(tmpdir(), "logistinfra-continuity-"));
    const path = join(dir, "state.json");
    const state = seed();
    state.transitions.push({
      id: "wait-1",
      workstreamId: "ws-waiting",
      mission: "obtain external proof",
      fromState: "message_sent",
      toState: "reply_received",
      action: "check for reply",
      operator: "message_triage",
      owner: "Taha",
      status: "pending",
      priority: 999,
      receiptRequired: "external reply",
      doneWhen: "reply exists",
      interruptionWakeCondition: "external reply arrives",
      artifactRefs: [],
      evidenceRefs: [],
      dependsOn: [],
      createdAt: "2026-09-19T00:00:00.000Z",
    });
    await writeFile(path, JSON.stringify(state, null, 2));

    const store = new JsonContinuityStore(path);
    const result = await route(store, "obtain external proof");
    expect(result?.transitionId).toBe("t1");
  });
});
