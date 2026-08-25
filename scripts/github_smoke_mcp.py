from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from mcp.server import MCPServer

mcp = MCPServer("reality-github-smoke")


def _github_request(method: str, url: str, payload: dict | None = None) -> dict:
    token = os.environ["GITHUB_TOKEN"]
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "reality-ontology-runtime-smoke",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


@mcp.tool()
def create_probe_issue(marker: str) -> dict:
    """Create exactly one reversible GitHub issue carrying the supplied smoke-test marker."""
    repo = os.environ["GITHUB_REPOSITORY"]
    receipt_path = Path(os.environ["REALITY_SMOKE_RECEIPT"])
    body = (
        "Automated reversible Reality Ontology × Goose × MCP integration probe.\n\n"
        f"marker: {marker}\n"
        f"workflow_run: {os.environ.get('GITHUB_RUN_ID', 'local')}\n"
        "This issue is expected to be independently reread and then closed by the smoke workflow."
    )
    issue = _github_request(
        "POST",
        f"https://api.github.com/repos/{repo}/issues",
        {"title": f"[reality-mcp-smoke] {marker}", "body": body},
    )
    receipt = {
        "repository": repo,
        "number": issue["number"],
        "api_url": issue["url"],
        "html_url": issue["html_url"],
        "marker": marker,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt


if __name__ == "__main__":
    mcp.run(transport="stdio")
