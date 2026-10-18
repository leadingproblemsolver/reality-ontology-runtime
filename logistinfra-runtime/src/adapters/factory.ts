import { AnthropicJudge, type LLMJudge } from "./llm.js";
import { GithubApiClient, type GithubIssuesClient } from "./github.js";
import { SupabaseStateStore } from "./supabase-state-store.js";
import type { StateStore } from "./state-store.js";

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`missing required environment variable ${name}`);
  return value;
}

export function buildLiveGithubClient(): GithubIssuesClient {
  return new GithubApiClient(process.env.GITHUB_TOKEN);
}

export function buildLiveLLMJudge(): LLMJudge {
  return new AnthropicJudge(requireEnv("LLM_API_KEY"), process.env.LLM_MODEL || "claude-sonnet-5");
}

export function buildLiveStateStore(): StateStore {
  return new SupabaseStateStore(requireEnv("SUPABASE_URL"), requireEnv("SUPABASE_SERVICE_ROLE_KEY"));
}
