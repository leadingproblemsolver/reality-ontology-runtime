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
    parser.add_argument("--repository", required=True)
    parser.add_argument("--reconcile-seconds", type=float, default=12.0)
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else None
    repo = args.repository
    expected_title = f"[reality-mcp-smoke] {args.marker}"
    list_url = f"https://api.github.com/repos/{repo}/issues?" + urllib.parse.urlencode(
        {"state": "all", "per_page": 100}
    )

    # Reconcile external reads only. A missing local receipt never authorizes replaying
    # the side-effecting create operation.
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

    if len(matching) != 1:
        print(json.dumps({
            "verified": False,
            "receipt_present": receipt is not None,
            "marker": args.marker,
            "matching_issue_count": len(matching),
            "reconcile_reads": reconcile_reads,
        }, sort_keys=True))
        return 1

    issue_url = matching[0].get("url")
    issue = _get_json(issue_url)
    if not isinstance(issue, dict):
        print("verification failed: direct issue reread returned unexpected payload")
        return 3

    body = issue.get("body") or ""
    title = issue.get("title") or ""
    receipt_consistent = True
    if receipt is not None:
        receipt_consistent = (
            receipt.get("repository") == repo
            and receipt.get("marker") == args.marker
            and receipt.get("number") == issue.get("number")
            and receipt.get("api_url") == issue.get("url")
        )

    verified = (
        issue.get("state") == "open"
        and title == expected_title
        and args.marker in body
        and matching[0].get("number") == issue.get("number")
        and receipt_consistent
    )
    print(json.dumps({
        "verified": verified,
        "receipt_present": receipt is not None,
        "issue_number": issue.get("number"),
        "html_url": issue.get("html_url"),
        "state": issue.get("state"),
        "marker": args.marker,
        "matching_issue_count": len(matching),
        "reconcile_reads": reconcile_reads,
    }, sort_keys=True))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
