import Anthropic from "@anthropic-ai/sdk";
import type { TextWorkerInvocation, TextWorkerInvoker, TextWorkerResult } from "./model-worker.js";

type FetchLike = typeof fetch;

function ensureOk(response: Response, body: string): void {
  if (!response.ok) {
    throw new Error(`provider request failed: ${response.status} ${response.statusText}: ${body.slice(0, 500)}`);
  }
}

export class AnthropicTextInvoker implements TextWorkerInvoker {
  readonly id = "anthropic";
  private readonly client: Anthropic;

  constructor(
    apiKey: string,
    public readonly model: string,
  ) {
    this.client = new Anthropic({ apiKey });
  }

  async invoke(input: TextWorkerInvocation): Promise<TextWorkerResult> {
    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: input.maxTokens ?? 2048,
      messages: [{ role: "user", content: input.prompt }],
    });

    const text = response.content
      .filter((block) => block.type === "text")
      .map((block) => block.type === "text" ? block.text : "")
      .join("\n");

    return {
      text,
      raw: { id: response.id, stopReason: response.stop_reason ?? null },
      providerRequestId: response.id,
    };
  }
}

export class GeminiTextInvoker implements TextWorkerInvoker {
  readonly id = "gemini";

  constructor(
    private readonly apiKey: string,
    public readonly model: string,
    private readonly fetchImpl: FetchLike = fetch,
  ) {}

  async invoke(input: TextWorkerInvocation): Promise<TextWorkerResult> {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(this.model)}:generateContent`;
    const response = await this.fetchImpl(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": this.apiKey,
      },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: input.prompt }] }],
        generationConfig: input.maxTokens ? { maxOutputTokens: input.maxTokens } : undefined,
      }),
    });

    const body = await response.text();
    ensureOk(response, body);
    const parsed = JSON.parse(body) as {
      candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
      responseId?: string;
    };
    const text = parsed.candidates?.[0]?.content?.parts
      ?.map((part) => part.text ?? "")
      .join("\n") ?? "";

    return {
      text,
      raw: parsed as Record<string, unknown>,
      providerRequestId: parsed.responseId ?? null,
    };
  }
}

export class OpenAIResponsesInvoker implements TextWorkerInvoker {
  readonly id = "openai";

  constructor(
    private readonly apiKey: string,
    public readonly model: string,
    private readonly fetchImpl: FetchLike = fetch,
    private readonly baseUrl = "https://api.openai.com/v1",
  ) {}

  async invoke(input: TextWorkerInvocation): Promise<TextWorkerResult> {
    const response = await this.fetchImpl(`${this.baseUrl}/responses`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.model,
        input: input.prompt,
        max_output_tokens: input.maxTokens,
      }),
    });

    const body = await response.text();
    ensureOk(response, body);
    const parsed = JSON.parse(body) as {
      id?: string;
      output_text?: string;
      output?: Array<{ content?: Array<{ type?: string; text?: string }> }>;
    };
    const text = parsed.output_text
      ?? parsed.output?.flatMap((item) => item.content ?? [])
        .filter((part) => part.type === "output_text")
        .map((part) => part.text ?? "")
        .join("\n")
      ?? "";

    return {
      text,
      raw: parsed as Record<string, unknown>,
      providerRequestId: parsed.id ?? null,
    };
  }
}

export class OpenAICompatibleChatInvoker implements TextWorkerInvoker {
  readonly id = "openai-compatible";

  constructor(
    private readonly apiKey: string,
    public readonly model: string,
    private readonly baseUrl: string,
    private readonly fetchImpl: FetchLike = fetch,
  ) {}

  async invoke(input: TextWorkerInvocation): Promise<TextWorkerResult> {
    const response = await this.fetchImpl(`${this.baseUrl.replace(/\/$/, "")}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.model,
        messages: [{ role: "user", content: input.prompt }],
        max_tokens: input.maxTokens,
      }),
    });

    const body = await response.text();
    ensureOk(response, body);
    const parsed = JSON.parse(body) as {
      id?: string;
      choices?: Array<{ message?: { content?: string } }>;
    };
    const text = parsed.choices?.[0]?.message?.content ?? "";

    return {
      text,
      raw: parsed as Record<string, unknown>,
      providerRequestId: parsed.id ?? null,
    };
  }
}
