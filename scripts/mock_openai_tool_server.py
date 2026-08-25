from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = int(os.environ.get("REALITY_MOCK_OPENAI_PORT", "8765"))
MODEL = os.environ.get("GOOSE_MODEL", "gpt-4o")
MARKER = os.environ.get("REALITY_SMOKE_MARKER", "reality-goose-mcp-smoke")


def _tool_name(payload: dict) -> str:
    tools = payload.get("tools") or []
    names = [t.get("function", {}).get("name") for t in tools if t.get("type") == "function"]
    names = [n for n in names if n]
    for name in names:
        if "create_probe_issue" in name:
            return name
    if not names:
        raise RuntimeError("Goose request did not expose an MCP tool")
    return names[0]


def _has_tool_result(payload: dict) -> bool:
    return any(message.get("role") == "tool" for message in payload.get("messages") or [])


class Handler(BaseHTTPRequestHandler):
    server_version = "RealityMockOpenAI/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print("mock-openai:", fmt % args, flush=True)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"ok": True})
            return
        if self.path.endswith("/models"):
            self._json(200, {"object": "list", "data": [{"id": MODEL, "object": "model"}]})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not self.path.endswith("/chat/completions"):
            self._json(404, {"error": f"unsupported path: {self.path}"})
            return

        final = _has_tool_result(payload)
        if payload.get("stream"):
            self._stream_chat(payload, final)
        else:
            self._json(200, self._chat_response(payload, final))

    def _chat_response(self, payload: dict, final: bool) -> dict:
        if final:
            message = {"role": "assistant", "content": "External MCP mutation observed; stop."}
            finish = "stop"
        else:
            name = _tool_name(payload)
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_reality_smoke",
                        "type": "function",
                        "function": {"name": name, "arguments": json.dumps({"marker": MARKER})},
                    }
                ],
            }
            finish = "tool_calls"
        return {
            "id": "chatcmpl-reality-smoke",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL,
            "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    def _stream_chat(self, payload: dict, final: bool) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        created = int(time.time())
        if final:
            chunks = [
                {
                    "id": "chatcmpl-reality-smoke",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL,
                    "choices": [{"index": 0, "delta": {"role": "assistant", "content": "External MCP mutation observed; stop."}, "finish_reason": None}],
                },
                {
                    "id": "chatcmpl-reality-smoke",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                },
            ]
        else:
            name = _tool_name(payload)
            chunks = [
                {
                    "id": "chatcmpl-reality-smoke",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "tool_calls": [
                                    {
                                        "index": 0,
                                        "id": "call_reality_smoke",
                                        "type": "function",
                                        "function": {"name": name, "arguments": json.dumps({"marker": MARKER})},
                                    }
                                ],
                            },
                            "finish_reason": None,
                        }
                    ],
                },
                {
                    "id": "chatcmpl-reality-smoke",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
                },
            ]

        for chunk in chunks:
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
            self.wfile.flush()
        usage = {
            "id": "chatcmpl-reality-smoke",
            "object": "chat.completion.chunk",
            "created": created,
            "model": MODEL,
            "choices": [],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }
        self.wfile.write(f"data: {json.dumps(usage)}\n\n".encode("utf-8"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"mock OpenAI-compatible provider listening on http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
