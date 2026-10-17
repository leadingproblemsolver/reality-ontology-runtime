import { task } from "@trigger.dev/sdk/v3";
import { buildLiveStateStore } from "../adapters/factory.js";
import { prepareInvestigation } from "../pipelines/github_opportunity/prepare.js";

/**
 * Manually invoked (never scheduled) -- only runs once a human has recorded
 * an "approved" decision for the given execution via the `decide` CLI/task.
 * Performs no GitHub mutation; it only assembles and persists the
 * investigation packet as evidence.
 */
export const investigateIssue = task({
  id: "logistinfra-prepare-investigation",
  run: async (payload: { executionId: string }) => {
    const store = buildLiveStateStore();
    return prepareInvestigation({ executionId: payload.executionId, store });
  },
});
