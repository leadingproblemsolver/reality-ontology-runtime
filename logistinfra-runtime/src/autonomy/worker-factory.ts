import type { ToolAdapter } from "./types.js";
import { createModelWorkerAdapter } from "./model-worker.js";
import {
  AnthropicTextInvoker,
  GeminiTextInvoker,
  OpenAICompatibleChatInvoker,
  OpenAIResponsesInvoker,
} from "./providers.js";

export interface WorkerEnv {
  ANTHROPIC_API_KEY?: string;
  ANTHROPIC_MODEL?: string;
  OPENAI_API_KEY?: string;
  OPENAI_MODEL?: string;
  GEMINI_API_KEY?: string;
  GEMINI_MODEL?: string;
  DEEPSEEK_API_KEY?: string;
  DEEPSEEK_MODEL?: string;
  DEEPSEEK_BASE_URL?: string;
}

export function buildConfiguredModelWorkers(env: WorkerEnv = process.env): Map<string, ToolAdapter> {
  const tools = new Map<string, ToolAdapter>();

  if (env.ANTHROPIC_API_KEY) {
    const invoker = new AnthropicTextInvoker(env.ANTHROPIC_API_KEY, env.ANTHROPIC_MODEL ?? "claude-sonnet-5");
    const adapter = createModelWorkerAdapter({
      ref: "tool:anthropic-reason",
      invoker,
      capabilities: ["reason.complex", "research.synthesize", "artifact.compile", "repo.reconstruct"],
      costRank: 30,
      qualityRank: 95,
    });
    tools.set(adapter.ref, adapter);
  }

  if (env.OPENAI_API_KEY) {
    const invoker = new OpenAIResponsesInvoker(env.OPENAI_API_KEY, env.OPENAI_MODEL ?? "gpt-5");
    const adapter = createModelWorkerAdapter({
      ref: "tool:openai-reason",
      invoker,
      capabilities: ["reason.complex", "cross_app.orchestrate", "research.synthesize", "artifact.compile", "verification.review"],
      costRank: 40,
      qualityRank: 100,
    });
    tools.set(adapter.ref, adapter);
  }

  if (env.GEMINI_API_KEY) {
    const invoker = new GeminiTextInvoker(env.GEMINI_API_KEY, env.GEMINI_MODEL ?? "gemini-3.8-flash");
    const adapter = createModelWorkerAdapter({
      ref: "tool:gemini-context",
      invoker,
      capabilities: ["context.long", "multimodal.audit", "corpus.reconstruct", "batch.review", "research.synthesize"],
      costRank: 15,
      qualityRank: 85,
    });
    tools.set(adapter.ref, adapter);
  }

  if (env.DEEPSEEK_API_KEY) {
    const invoker = new OpenAICompatibleChatInvoker(
      env.DEEPSEEK_API_KEY,
      env.DEEPSEEK_MODEL ?? "deepseek-chat",
      env.DEEPSEEK_BASE_URL ?? "https://api.deepseek.com",
    );
    const adapter = createModelWorkerAdapter({
      ref: "tool:deepseek-batch",
      invoker,
      capabilities: ["batch.transform", "batch.extract", "batch.classify", "research.preprocess"],
      costRank: 5,
      qualityRank: 75,
    });
    tools.set(adapter.ref, adapter);
  }

  return tools;
}
