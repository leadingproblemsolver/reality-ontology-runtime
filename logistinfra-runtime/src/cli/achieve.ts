import { readFile } from "node:fs/promises";
import { integrateOutcome } from "../autonomy/integrator.js";
import type { CapabilityDescriptor, OutcomeContract } from "../autonomy/capabilities.js";

function arg(name: string): string | null {
  const index = process.argv.indexOf(name);
  return index >= 0 ? (process.argv[index + 1] ?? null) : null;
}

async function readJson<T>(path: string): Promise<T> {
  return JSON.parse(await readFile(path, "utf8")) as T;
}

async function main(): Promise<void> {
  const specPath = arg("--spec");
  const registryPath = arg("--registry");
  if (!specPath || !registryPath) {
    throw new Error("usage: achieve --spec <outcome.json> --registry <capabilities.json>");
  }

  const contract = await readJson<OutcomeContract>(specPath);
  const rawRegistry = await readJson<{ capabilities?: CapabilityDescriptor[] } | CapabilityDescriptor[]>(registryPath);
  const registry = Array.isArray(rawRegistry) ? rawRegistry : (rawRegistry.capabilities ?? []);

  const plan = integrateOutcome(contract, registry);
  console.log(JSON.stringify(plan, null, 2));

  if (plan.unresolvedRequirements.length > 0) process.exitCode = 2;
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
