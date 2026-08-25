from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path


def _request(method: str, url: str, payload: dict | None = None) -> object:
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
            "User-Agent": "reality-ontology-runtime-cleanup",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--marker")
    parser.add_argument("--repository")
    parser.add_argument("--reconcile-seconds", type=float, default=12.0)
    args = parser.parse_args()

    path = Path(args.receipt)
    issue_url = None
    if path.is_file():
        receipt = json.loads(path.read_text(encoding="utf-8"))
        issue_url = receipt.get("api_url")

    if issue_url is None and args.marker and args.repository:
        expected_title = f"[reality-mcp-smoke] {args.marker}"
        list_url = f"https://api.github.com/repos/{args.repository}/issues?" + urllib.parse.urlencode(
            {"state": "all", "per_page": 100}
        )
        deadline = time.monotonic() + max(0.0, args.reconcile_seconds)
        while True:
            listed = _request("GET", list_url)
            matching = [
                item for item in listed
                if isinstance(item, dict) and item.get("title") == expected_title
            ] if isinstance(listed, list) else []
            if len(matching) == 1:
                issue_url = matching[0].get("url")
                break
            if time.monotonic() >= deadline:
                print(json.dumps({"closed": False, "reason": "probe issue not uniquely discoverable"}))
                return 1
            time.sleep(0.5)

    if issue_url is None:
        print("no smoke issue receipt or discovery coordinates; nothing to close")
        return 0

    issue = _request("PATCH", issue_url, {"state": "closed", "state_reason": "completed"})
    print(json.dumps({"closed": isinstance(issue, dict) and issue.get("state") == "closed", "html_url": issue.get("html_url") if isinstance(issue, dict) else None}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
