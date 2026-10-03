import { readFile } from "node:fs/promises";
import { JsonContinuityStore } from "../continuity/store.js";
import { route, settle, sync } from "../continuity/engine.js";
import type { Receipt } from "../continuity/types.js";

function arg(name: string): string | null {
  const index = process.argv.indexOf(name);
  return index >= 0 ? (process.argv[index + 1] ?? null) : null;
}

async function main(): Promise<void> {
  const operation = process.argv[2];
  const statePath = arg("--state") ?? "continuity-state.json";
  const store = new JsonContinuityStore(statePath);

  if (operation === "sync") {
    console.log(JSON.stringify(await sync(store), null, 2));
    return;
  }

  if (operation === "route") {
    const mission = arg("--mission");
    if (!mission) throw new Error("--mission is required");
    console.log(JSON.stringify(await route(store, mission), null, 2));
    return;
  }

  if (operation === "settle") {
    const receiptFile = arg("--receipt");
    if (!receiptFile) throw new Error("--receipt is required");
    const receipt = JSON.parse(await readFile(receiptFile, "utf8")) as Receipt;
    const state = await settle(store, receipt);
    console.log(JSON.stringify({ status: "settled", updatedAt: state.updatedAt }, null, 2));
    return;
  }

  throw new Error("usage: continuity <sync|route|settle> --state <path> [--mission <text> | --receipt <file>]");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
