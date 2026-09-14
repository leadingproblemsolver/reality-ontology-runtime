import { buildLiveStateStore } from "../adapters/factory.js";
import { decideInvestigation } from "../pipelines/github_opportunity/approval.js";
import type { ApprovalDecision } from "../types.js";

function parseArgs(argv: string[]): { executionId: string; decision: ApprovalDecision } {
  const executionId = argv.find((arg) => arg.startsWith("--execution="))?.split("=")[1];
  const decisionRaw = argv.find((arg) => arg.startsWith("--decision="))?.split("=")[1];

  if (!executionId) throw new Error("usage: npm run decide -- --execution=<id> --decision=approved|rejected");
  if (decisionRaw !== "approved" && decisionRaw !== "rejected") {
    throw new Error(`--decision must be "approved" or "rejected", got: ${decisionRaw}`);
  }

  return { executionId, decision: decisionRaw };
}

async function main() {
  const { executionId, decision } = parseArgs(process.argv.slice(2));
  const store = buildLiveStateStore();
  await decideInvestigation({ executionId, decision, store });
  console.log(`recorded decision "${decision}" for execution ${executionId}`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
