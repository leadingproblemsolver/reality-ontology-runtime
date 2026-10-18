import type { ContextPacket } from "../continuity/types.js";
import type { ToolAdapter } from "./types.js";

export interface ResolvedTool {
  selector: string;
  toolRef: string;
  tool: ToolAdapter;
}

function compareCandidates(a: ToolAdapter, b: ToolAdapter): number {
  const cost = (a.costRank ?? 100) - (b.costRank ?? 100);
  if (cost !== 0) return cost;

  const quality = (b.qualityRank ?? 0) - (a.qualityRank ?? 0);
  if (quality !== 0) return quality;

  return a.ref.localeCompare(b.ref);
}

/**
 * Resolve an executable adapter without hard-coding provider identity into routing.
 *
 * Selectors are evaluated in transition order:
 * - exact tool refs (for example "tool:github.write")
 * - capability selectors (for example "cap:code.execute")
 *
 * Capability selectors choose the lowest-cost registered adapter first, then the
 * highest quality rank, preserving deterministic tie-breaking by ref.
 *
 * Authority is still enforced by the autonomous engine after resolution.
 */
export function resolveTool(
  context: ContextPacket,
  tools: Map<string, ToolAdapter>,
): ResolvedTool | null {
  for (const selector of context.toolRefs) {
    const exact = tools.get(selector);
    if (exact) {
      return { selector, toolRef: exact.ref, tool: exact };
    }

    if (!selector.startsWith("cap:")) continue;
    const capability = selector.slice("cap:".length).trim();
    if (!capability) continue;

    const candidates = [...tools.values()]
      .filter((tool) => tool.capabilities?.includes(capability))
      .sort(compareCandidates);

    const selected = candidates[0];
    if (selected) {
      return { selector, toolRef: selected.ref, tool: selected };
    }
  }

  return null;
}
