import { describe, expect, it } from "vitest";
import { InMemoryStateStore } from "../src/adapters/state-store.js";
import { acquireAndPersistSignals } from "../src/pipelines/github_opportunity/scout.js";
import { buildFixtureIssues } from "./fixtures/browser-use-issues.js";
import { FixtureGithubClient, ThrowingGithubClient } from "./fakes.js";

describe("acquireAndPersistSignals", () => {
  it("normalizes issues, skips pull requests, and persists one signal per issue", async () => {
    const store = new InMemoryStateStore();
    const client = new FixtureGithubClient(buildFixtureIssues());

    const result = await acquireAndPersistSignals({ owner: "browser-use", repo: "browser-use", githubClient: client, store });

    // 6 fixture entries, 1 is a pull request and must be skipped entirely.
    expect(result.signals.length).toBe(5);
    expect(result.malformed.length).toBe(0);
    expect(store.listSignals().length).toBe(5);
  });

  it("is idempotent across reruns: no duplicate signals for the same source_id", async () => {
    const store = new InMemoryStateStore();
    const client = new FixtureGithubClient(buildFixtureIssues());

    const first = await acquireAndPersistSignals({ owner: "browser-use", repo: "browser-use", githubClient: client, store });
    const second = await acquireAndPersistSignals({ owner: "browser-use", repo: "browser-use", githubClient: client, store });

    expect(store.listSignals().length).toBe(first.signals.length);
    const firstIds = new Set(first.signals.map((s) => s.signalId));
    const secondIds = new Set(second.signals.map((s) => s.signalId));
    expect(secondIds).toEqual(firstIds);
  });

  it("persists a malformed-signal evidence entry for an individual bad issue without aborting the run", async () => {
    const store = new InMemoryStateStore();
    const malformedEntry = { number: 999, title: "missing required fields" }; // no id, html_url, state, etc.
    const client = new FixtureGithubClient([...buildFixtureIssues(), malformedEntry]);

    const result = await acquireAndPersistSignals({ owner: "browser-use", repo: "browser-use", githubClient: client, store });

    expect(result.malformed.length).toBe(1);
    expect(result.signals.length).toBe(5);
    const evidence = store.listEvidence().filter((e) => e.source === "github" && e.doesNotProve?.includes("ingestion failed"));
    expect(evidence.length).toBe(1);
  });

  it("propagates a total GitHub API failure instead of silently returning nothing", async () => {
    const store = new InMemoryStateStore();
    const client = new ThrowingGithubClient();

    await expect(
      acquireAndPersistSignals({ owner: "browser-use", repo: "browser-use", githubClient: client, store }),
    ).rejects.toThrow(/503/);
  });
});
