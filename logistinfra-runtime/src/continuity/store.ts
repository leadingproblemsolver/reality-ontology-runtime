import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import type { GlobalState } from "./types.js";

export interface ContinuityStore {
  load(): Promise<GlobalState>;
  save(state: GlobalState): Promise<void>;
}

export class JsonContinuityStore implements ContinuityStore {
  constructor(private readonly path: string) {}

  async load(): Promise<GlobalState> {
    const raw = await readFile(this.path, "utf8");
    const state = JSON.parse(raw) as GlobalState;
    if (state.version !== 1) throw new Error(`unsupported continuity state version: ${String(state.version)}`);
    return state;
  }

  async save(state: GlobalState): Promise<void> {
    await mkdir(dirname(this.path), { recursive: true });
    const temp = `${this.path}.tmp`;
    await writeFile(temp, JSON.stringify(state, null, 2) + "\n", "utf8");
    await rename(temp, this.path);
  }
}
