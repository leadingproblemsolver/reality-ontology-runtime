import type { GithubIssuesClient } from "../../adapters/github.js";
import type { StateStore } from "../../adapters/state-store.js";
import type { NormalizedIssue } from "../../types.js";
import { normalizeIssue } from "./normalize.js";

export interface AcquiredSignal {
  signalId: string;
  issue: NormalizedIssue;
}

export interface MalformedIssue {
  raw: unknown;
  error: string;
}

export interface AcquireResult {
  signals: AcquiredSignal[];
  malformed: MalformedIssue[];
}

/**
 * Fetches open issues, normalizes them, and idempotently persists each as a
 * `signals` row keyed on (source, source_id). Individual malformed issues are
 * recorded as evidence rather than aborting the whole run.
 */
export async function acquireAndPersistSignals(params: {
  owner: string;
  repo: string;
  githubClient: GithubIssuesClient;
  store: StateStore;
}): Promise<AcquireResult> {
  const rawIssues = await params.githubClient.listOpenIssues({ owner: params.owner, repo: params.repo });

  const signals: AcquiredSignal[] = [];
  const malformed: MalformedIssue[] = [];

  for (const raw of rawIssues) {
    if (raw && typeof raw === "object" && "pull_request" in raw) continue;

    const result = normalizeIssue(raw, { owner: params.owner, repo: params.repo });
    if (!result.ok) {
      malformed.push({ raw, error: result.error });
      await params.store.recordEvidence({
        executionId: null,
        signalId: null,
        source: "github",
        observation: { raw },
        proves: null,
        doesNotProve: `signal ingestion failed: ${result.error}`,
      });
      continue;
    }

    const { id } = await params.store.upsertSignal({
      source: "github",
      sourceId: result.issue.sourceId,
      sourceUrl: result.issue.url,
      observation: { normalized: result.issue, raw },
    });

    signals.push({ signalId: id, issue: result.issue });
  }

  return { signals, malformed };
}
