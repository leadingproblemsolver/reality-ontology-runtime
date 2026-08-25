from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path


def _get_json(url: str) -> object:
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "reality-ontology-runtime-verifier",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--marker", required=True)
    parser.add_argument("--reconcile-seconds", type=float, default=10.0)
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    if not receipt_path.is_file():
        print("verification failed: MCP transport receipt is missing")
        return 2

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    issue = _get_json(receipt["api_url"])
    if not isinstance(issue, dict):
        print("verification failed: issue reread returned unexpected payload")
        return 3

    repo = receipt["repository"]
    list_url = f"https://api.github.com/repos/{repo}/issues?" + urllib.parse.urlencode(
        {"state": "all", "per_page": 100}
    )
    expected_title = f"[reality-mcp-smoke] {args.marker}"

    # Collection/list reads can trail the direct resource GET. Reconcile by rereading
    # external state only; never repeat the side-effecting create operation.
    deadline = time.monotonic() + max(0.0, args.reconcile_seconds)
    matching: list[dict] = []
    reconcile_reads = 0
    while True:
        reconcile_reads += 1
        listed = _get_json(list_url)
        matching = [
            item for item in listed
            if isinstance(item, dict) and item.get("title") == expected_title
        ] if isinstance(listed, list) else []
        if len(matching) == 1 or time.monotonic() >= deadline:
            break
        time.sleep(0.5)

    body = issue.get("body") or ""
    title = issue.get("title") or ""
    verified = (
        issue.get("state") == "open"
        and args.marker == receipt.get("marker")
        and args.marker in body
        and args.marker in title
        and issue.get("number") == receipt.get("number")
        and len(matching) == 1
        and matching[0].get("number") == receipt.get("number")
    )
    print(
        json.dumps(
            {
                "verified": verified,
                "issue_number": issue.get("number"),
                "html_url": issue.get("html_url"),
                "state": issue.get("state"),
                "marker": args.marker,
                "matching_issue_count": len(matching),
                "reconcile_reads": reconcile_reads,
            },
            sort_keys=True,
        )
    )
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
