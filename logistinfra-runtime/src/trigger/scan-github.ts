import { schedules } from "@trigger.dev/sdk/v3";
import { buildLiveGithubClient, buildLiveLLMJudge, buildLiveStateStore } from "../adapters/factory.js";
import { runOpportunityScan } from "../pipelines/github_opportunity/pipeline.js";

/**
 * Scheduled entry point once this repo is wired to a Trigger.dev project.
 * GitHub Actions (.github/workflows/logistinfra-opportunity-scan.yml) already
 * runs the same underlying pipeline hourly via `npm run scan`; this task
 * exists so the same logic can move to Trigger.dev without a rewrite once
 * queues/durable waits/retries are actually needed (see logistinfra-runtime/README.md).
 */
export const scanGithubOpportunities = schedules.task({
  id: "logistinfra-scan-browser-use-issues",
  cron: "17 * * * *",
  run: async () => {
    const store = buildLiveStateStore();
    const githubClient = buildLiveGithubClient();
    const llm = buildLiveLLMJudge();

    const result = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });
    if (result.status === "failed") {
      throw new Error(`opportunity scan failed: ${result.error}`);
    }
    return result;
  },
});
