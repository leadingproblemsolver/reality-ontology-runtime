from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--marker", required=True)
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    if not receipt_path.is_file():
        print("verification failed: MCP transport receipt is missing")
        return 2

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        receipt["api_url"],
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "reality-ontology-runtime-verifier",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        issue = json.loads(resp.read().decode("utf-8"))

    body = issue.get("body") or ""
    title = issue.get("title") or ""
    verified = (
        issue.get("state") == "open"
        and args.marker == receipt.get("marker")
        and args.marker in body
        and args.marker in title
        and issue.get("number") == receipt.get("number")
    )
    print(
        json.dumps(
            {
                "verified": verified,
                "issue_number": issue.get("number"),
                "html_url": issue.get("html_url"),
                "state": issue.get("state"),
                "marker": args.marker,
            },
            sort_keys=True,
        )
    )
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
