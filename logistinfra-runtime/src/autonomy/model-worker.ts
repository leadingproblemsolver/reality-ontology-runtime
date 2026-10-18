import { createHash } from "node:crypto";
import type { ToolAdapter, ToolCallRequest, ToolCallResult, VerificationResult } from "./types.js";

export interface TextWorkerInvocation {
  prompt: string;
  maxTokens?: number;
}

export interface TextWorkerResult {
  text: string;
  raw: Record<string, unknown>;
  providerRequestId?: string | null;
}

export interface TextWorkerInvoker {
  id: string;
  model: string;
  invoke(input: TextWorkerInvocation): Promise<TextWorkerResult>;
}

export interface ModelWorkerAdapterOptions {
  ref: string;
  invoker: TextWorkerInvoker;
  capabilities: string[];
  costRank?: number;
  qualityRank?: number;
  maxTokens?: number;
}

function compilePrompt(request: ToolCallRequest): string {
  const c = request.context;
  return [
    "You are an execution worker inside Logistinfra. You do not own priority, truth, or settlement.",
    "Perform only the bounded action below. Preserve uncertainty. Do not claim external effects you cannot observe.",
    "",
    `MISSION: ${c.mission}`,
    `ACTION: ${request.action}`,
    `DONE WHEN: ${c.doneWhen}`,
    `REQUIRED RECEIPT: ${c.requiredReceipt}`,
    `CURRENT TRUTH:\n- ${c.currentTruth.join("\n- ")}`,
    `FROZEN DECISIONS:\n- ${c.frozenDecisions.join("\n- ")}`,
    `EVIDENCE REFS:\n- ${c.evidenceRefs.join("\n- ")}`,
    `ARTIFACT REFS:\n- ${c.artifactRefs.join("\n- ")}`,
    "",
    "Return an inspectable artifact/result only. External state changes must be performed and verified by dedicated surface adapters.",
  ].join("\n");
}

function artifactHash(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

/**
 * Provider-neutral LLM worker adapter.
 *
 * This adapter can only prove that an inspectable worker artifact was produced.
 * It deliberately cannot prove external state change, merge, send, deployment,
 * payment, or any other consequential effect.
 */
export function createModelWorkerAdapter(options: ModelWorkerAdapterOptions): ToolAdapter {
  return {
    ref: options.ref,
    authority: "read",
    capabilities: options.capabilities,
    costRank: options.costRank,
    qualityRank: options.qualityRank,

    async execute(request: ToolCallRequest): Promise<ToolCallResult> {
      const result = await options.invoker.invoke({
        prompt: compilePrompt(request),
        maxTokens: options.maxTokens,
      });

      if (!result.text.trim()) {
        return {
          ok: false,
          raw: result.raw,
          externalRef: result.providerRequestId ?? null,
          error: "worker returned empty output",
        };
      }

      return {
        ok: true,
        raw: {
          workerId: options.invoker.id,
          model: options.invoker.model,
          text: result.text,
          artifactSha256: artifactHash(result.text),
          providerRaw: result.raw,
        },
        externalRef: result.providerRequestId ?? null,
      };
    },

    async verify(_request: ToolCallRequest, execution: ToolCallResult): Promise<VerificationResult> {
      const text = typeof execution.raw.text === "string" ? execution.raw.text : "";
      const hash = typeof execution.raw.artifactSha256 === "string" ? execution.raw.artifactSha256 : "";

      if (!text.trim() || !hash || artifactHash(text) !== hash) {
        return {
          verified: false,
          observation: {
            workerId: execution.raw.workerId,
            model: execution.raw.model,
            artifactPresent: Boolean(text.trim()),
            hashMatches: false,
          },
          proves: null,
          doesNotProve: "inspectable worker artifact could not be verified",
        };
      }

      return {
        verified: true,
        observation: {
          workerId: execution.raw.workerId,
          model: execution.raw.model,
          artifactSha256: hash,
          artifactLength: text.length,
        },
        proves: "an inspectable worker artifact was produced and its content hash was independently recomputed",
        doesNotProve: "semantic correctness or any external state change",
      };
    },
  };
}
