from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    path = Path(args.receipt)
    if not path.is_file():
        print("no smoke issue receipt; nothing to close")
        return 0

    receipt = json.loads(path.read_text(encoding="utf-8"))
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        receipt["api_url"],
        data=json.dumps({"state": "closed", "state_reason": "completed"}).encode("utf-8"),
        method="PATCH",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "reality-ontology-runtime-cleanup",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        issue = json.loads(resp.read().decode("utf-8"))
    print(json.dumps({"closed": issue.get("state") == "closed", "html_url": issue.get("html_url")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
