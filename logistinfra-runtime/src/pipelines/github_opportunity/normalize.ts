import { z } from "zod";
import type { RawGithubIssue } from "../../adapters/github.js";
import type { NormalizedIssue } from "../../types.js";

const RawIssueSchema = z.object({
  id: z.number(),
  number: z.number(),
  title: z.string(),
  body: z.string().nullable(),
  html_url: z.string(),
  state: z.string(),
  labels: z.array(z.union([z.string(), z.object({ name: z.string().optional() })])),
  created_at: z.string(),
  updated_at: z.string(),
  comments: z.number(),
  user: z.object({ login: z.string().optional() }).nullable(),
});

export type NormalizeResult =
  | { ok: true; issue: NormalizedIssue }
  | { ok: false; error: string };

export function normalizeIssue(
  raw: unknown,
  target: { owner: string; repo: string },
): NormalizeResult {
  const parsed = RawIssueSchema.safeParse(raw);
  if (!parsed.success) {
    return { ok: false, error: parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ") };
  }
  const value = parsed.data as RawGithubIssue;

  const labels = value.labels
    .map((label) => (typeof label === "string" ? label : label.name))
    .filter((label): label is string => Boolean(label));

  const issue: NormalizedIssue = {
    sourceId: `${target.owner}/${target.repo}#${value.number}`,
    owner: target.owner,
    repo: target.repo,
    number: value.number,
    title: value.title,
    body: value.body ?? "",
    url: value.html_url,
    state: value.state,
    labels,
    authorLogin: value.user?.login ?? null,
    commentsCount: value.comments,
    createdAt: value.created_at,
    updatedAt: value.updated_at,
  };

  return { ok: true, issue };
}
