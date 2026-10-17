import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { JsonContinuityStore } from "../src/continuity/store.js";
import { route, sync } from "../src/continuity/engine.js";

describe("live bootstrap V0", () => {
  it("routes the live external adoption interrupt and suppresses waiting workstreams", async () => {
    const store = new JsonContinuityStore(join(process.cwd(), "bootstrap", "continuity.live.v0.json"));

    const state = await sync(store);
    expect(state.waiting.map((w) => w.id).sort()).toEqual([
      "ws-accountsignal-outbound",
      "ws-channel-partner",
    ]);
    expect(state.active.map((w) => w.id)).toContain("ws-langgraph-adoption");

    const packet = await route(store, "obtain external developer adoption evidence");
    expect(packet?.transitionId).toBe("t-langgraph-prep");
    expect(packet?.workstreamId).toBe("ws-langgraph-adoption");
    expect(packet?.chatReference).toContain("Creator Maintainer Externalization");
    expect(packet?.artifactRefs).toContain("https://github.com/langchain-ai/langgraph/issues/8464");
    expect(packet?.requiredReceipt).toContain("response draft");
  });

  it("keeps infrastructure closure independently routable", async () => {
    const store = new JsonContinuityStore(join(process.cwd(), "bootstrap", "continuity.live.v0.json"));
    const packet = await route(store, "eliminate context and execution friction");

    expect(packet?.transitionId).toBe("t-live-bindings");
    expect(packet?.toolRefs).toEqual(["tool:github", "tool:gmail", "tool:calendar"]);
  });
});
