import type { PersistedOpportunity } from "./persist.js";

/** Highest composite score first. Ties broken by lowest issue number (older/earlier first). */
export function rankOpportunities(opportunities: PersistedOpportunity[]): PersistedOpportunity[] {
  return [...opportunities].sort((a, b) => {
    if (b.composite !== a.composite) return b.composite - a.composite;
    return a.issue.number - b.issue.number;
  });
}
