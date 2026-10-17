import { buildLiveStateStore } from "../adapters/factory.js";
import { prepareInvestigation } from "../pipelines/github_opportunity/prepare.js";

function parseArgs(argv: string[]): { executionId: string } {
  const executionId = argv.find((arg) => arg.startsWith("--execution="))?.split("=")[1];
  if (!executionId) throw new Error("usage: npm run investigate -- --execution=<id>");
  return { executionId };
}

async function main() {
  const { executionId } = parseArgs(process.argv.slice(2));
  const store = buildLiveStateStore();
  const result = await prepareInvestigation({ executionId, store });
  console.log(JSON.stringify(result, null, 2));
  if (result.status !== "ready") process.exitCode = 1;
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
