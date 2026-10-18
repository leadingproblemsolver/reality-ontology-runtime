import { buildLiveGithubClient, buildLiveLLMJudge, buildLiveStateStore } from "../adapters/factory.js";
import { runOpportunityScan } from "../pipelines/github_opportunity/pipeline.js";

async function main() {
  const store = buildLiveStateStore();
  const githubClient = buildLiveGithubClient();
  const llm = buildLiveLLMJudge();

  const result = await runOpportunityScan({ owner: "browser-use", repo: "browser-use", githubClient, llm, store });
  console.log(JSON.stringify(result, null, 2));

  if (result.status === "failed") {
    process.exitCode = 1;
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
