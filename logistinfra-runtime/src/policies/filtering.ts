import type { NormalizedIssue } from "../types.js";

export interface FilterConfig {
  excludeLabels: string[];
  minBodyLength: number;
  maxAgeDaysSinceUpdate: number;
}

export const DEFAULT_FILTER_CONFIG: FilterConfig = {
  excludeLabels: ["duplicate", "wontfix", "invalid", "question", "enhancement", "documentation"],
  minBodyLength: 40,
  maxAgeDaysSinceUpdate: 180,
};

export interface FilterDecision {
  passes: boolean;
  reasons: string[];
}

export function evaluateFilter(
  issue: NormalizedIssue,
  config: FilterConfig = DEFAULT_FILTER_CONFIG,
  now: Date = new Date(),
): FilterDecision {
  const reasons: string[] = [];

  if (issue.state !== "open") {
    reasons.push(`issue state is "${issue.state}", not open`);
  }

  const bodyLength = issue.body.trim().length;
  if (bodyLength < config.minBodyLength) {
    reasons.push(`body too short to indicate a reproducible report (${bodyLength} chars, need ${config.minBodyLength})`);
  }

  const lowerLabels = issue.labels.map((label) => label.toLowerCase());
  const excludedHit = lowerLabels.filter((label) => config.excludeLabels.includes(label));
  if (excludedHit.length > 0) {
    reasons.push(`carries excluded label(s): ${excludedHit.join(", ")}`);
  }

  const updatedAt = new Date(issue.updatedAt);
  const ageDays = (now.getTime() - updatedAt.getTime()) / 86_400_000;
  if (Number.isFinite(ageDays) && ageDays > config.maxAgeDaysSinceUpdate) {
    reasons.push(`stale: last updated ${Math.round(ageDays)} days ago (limit ${config.maxAgeDaysSinceUpdate})`);
  }

  return { passes: reasons.length === 0, reasons };
}
