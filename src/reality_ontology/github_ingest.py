"""Read-only GitHub PR observation -> canonical Python RealityStore.

L0 ingestion. A GitHub snapshot is observed source data, never proof
that a deployment, acceptance, payment or external action occurred.
No external writes, no tool-acknowledgement promotion, no background jobs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import EpistemicType
from .store import RealityStore

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _validate_target(repo: str, number: int) -> str:
    if not _REPO.fullmatch(repo) or ".." in repo or not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("expected GitHub owner/repository and positive PR number")
    return f"https://github.com/{repo}/pull/{number}"


def fetch_github_pr(repo: str, number: int) -> dict[str, Any]:
    """Read exactly one PR from api.github.com; token is optional for public PRs."""
    _validate_target(repo, number)
    url = f"https://api.github.com/repos/{repo}/pulls/{number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "logistinfra-canonical-observer",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"GitHub read failed: HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("GitHub read failed: network unavailable") from exc
    if not isinstance(payload, dict):
        raise ValueError("GitHub returned a non-object PR")
    return payload


def _snapshot(raw: dict[str, Any], repo: str, number: int) -> dict[str, Any]:
    url = _validate_target(repo, number)
    if not isinstance(raw, dict):
        raise ValueError("PR payload must be an object")
    head = raw.get("head")
    base = raw.get("base")
    if raw.get("number") != number or raw.get("html_url") != url:
        raise ValueError("PR identity mismatch; no canonical ingest")
    if not isinstance(head, dict) or not isinstance(head.get("sha"), str) or not head["sha"]:
        raise ValueError("missing GitHub head.sha")
    if not isinstance(base, dict) or not isinstance(base.get("ref"), str):
        raise ValueError("missing GitHub base.ref")
    if raw.get("state") not in {"open", "closed"}:
        raise ValueError("unknown GitHub PR state")
    if not isinstance(raw.get("updated_at"), str) or not raw["updated_at"]:
        raise ValueError("missing source updated_at")
    if not isinstance(raw.get("title"), str):
        raise ValueError("missing PR title")
    if not isinstance(raw.get("draft"), bool):
        raise ValueError("missing PR draft status")
    return {
        "source": "api.github.com",
        "repo": repo,
        "number": number,
        "url": url,
        "head_sha": head["sha"],
        "base_ref": base["ref"],
        "state": raw["state"],
        "draft": raw["draft"],
        "updated_at": raw["updated_at"],
        "merged_at": raw.get("merged_at"),
        "title": raw["title"],
    }


def sync_github_pr(
    db_path: str | Path,
    repo: str,
    number: int,
    *,
    fetcher: Callable[[str, int], dict[str, Any]] = fetch_github_pr,
) -> dict[str, Any]:
    """Replay-safe read of one external source into the existing event ledger.

    Validate/fetch before opening DB. Stable event/evidence identities allow
    recovery if the process exits between evidence and event commits.
    """
    _validate_target(repo, number)
    snap = _snapshot(fetcher(repo, number), repo, number)
    observation = json.dumps(snap, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(observation.encode("utf-8")).hexdigest()
    # Both IDs include the full fingerprint; distinct source revisions never collide.
    evidence_id = "ev_ghpr_" + digest
    event_id = "evt_ghpr_" + digest
    with RealityStore(db_path) as store:
        actor_id = store.add_actor("github_read_observer", actor_type="service", actor_id="actor_github_read")
        object_id = store.add_object(f"github:pr:{repo}#{number}", "external_pull_request")
        already = store.db.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone()
        if already:
            status = "UNCHANGED"
        else:
            seen_evidence = store.db.execute(
                "SELECT 1 FROM evidence WHERE evidence_id=?", (evidence_id,)
            ).fetchone()
            if not seen_evidence:
                store.add_evidence(
                    "external_observation",
                    snap["url"],
                    observation,
                    evidence_id=evidence_id,
                    metadata={"provider": "github", "source_updated_at": snap["updated_at"], "sha256": digest},
                )
            # resulting_state=None is intentional: observation is NOT a truth-ladder promotion.
            store.record_event(
                actor_id=actor_id,
                object_id=object_id,
                event_type="external_pr_snapshot_observed",
                resulting_state=None,
                evidence_ids=[evidence_id],
                source="github.api.readonly",
                epistemic_type=EpistemicType.OBSERVATION,
                metadata={"source_updated_at": snap["updated_at"], "sha256": digest},
                event_id=event_id,
            )
            status = "NEW_OBSERVATION"
        return {
            "status": status,
            "source_url": snap["url"],
            "source_updated_at": snap["updated_at"],
            "snapshot_sha256": digest,
            "event_id": event_id,
            "evidence_id": evidence_id,
            "canonical_object_id": object_id,
            "claim_ceiling": "EXTERNAL_SOURCE_OBSERVED_ONLY",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Observe a GitHub PR in the canonical RealityStore (no external writes)")
    parser.add_argument("--db", default=os.environ.get("RO_DB", ".runtime/reality.db"))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        result = sync_github_pr(args.db, args.repo, args.pr)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
