"""Approval-bound GitHub issue-comment transition, with replay-safe verification.

No automatic sends. Approval belongs to the exact target and content hash.
A repeated request first rereads external comments and never reposts matching content.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from typing import Any, Protocol
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .store import RealityStore

TARGET = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TAG = "<!-- logistinfra-action:"
MAX_BODY = 10000


class GitHubClient(Protocol):
    def comments(self, repo: str, issue: int) -> list[dict[str, Any]]: ...
    def post(self, repo: str, issue: int, body: str) -> dict[str, Any]: ...


class GitHubCommentsAPI:
    def __init__(self, token: str | None = None):
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")

    def request(self, path: str, method: str = "GET", payload: dict | None = None):
        if method != "GET" and not self.token:
            raise PermissionError("GITHUB_TOKEN is required to post")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "logistinfra-approved-executor",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        data = json.dumps(payload).encode() if payload is not None else None
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = Request("https://api.github.com/" + path, data=data, method=method, headers=headers)
        try:
            with urlopen(req, timeout=15) as response:
                result = json.load(response)
        except HTTPError as exc:
            raise RuntimeError(f"GitHub HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("GitHub network read/write failed") from exc
        return result

    def comments(self, repo: str, issue: int) -> list[dict[str, Any]]:
        all_rows = []
        for page in range(1, 21):
            rows = self.request(f"repos/{repo}/issues/{issue}/comments?per_page=100&page={page}")
            if not isinstance(rows, list):
                raise RuntimeError("unexpected GitHub comments payload")
            all_rows.extend(rows)
            if len(rows) < 100:
                return all_rows
        raise RuntimeError("comment pagination limit exceeded: fail closed")

    def post(self, repo: str, issue: int, body: str) -> dict[str, Any]:
        result = self.request(f"repos/{repo}/issues/{issue}/comments", "POST", {"body": body})
        if not isinstance(result, dict):
            raise RuntimeError("unexpected GitHub post response")
        return result


def packet(repo: str, issue: int, message: str) -> dict[str, str | int]:
    if not TARGET.fullmatch(repo) or ".." in repo or not isinstance(issue, int) or isinstance(issue, bool) or issue < 1:
        raise ValueError("invalid GitHub issue target")
    if not isinstance(message, str) or not message.strip() or len(message) > MAX_BODY or TAG in message:
        raise ValueError("invalid or unsafe message")
    digest = hashlib.sha256(json.dumps([repo, issue, message], separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    return {
        "transition_id": "github_comment_" + digest,
        "repo": repo,
        "issue": issue,
        "message": message,
        "marker": f"{TAG}{digest} -->",
        "target_url": f"https://github.com/{repo}/issues/{issue}",
        "approval_required": "EXPLICIT_USER_APPROVAL_FOR_THIS_EXACT_PAYLOAD",
    }


def execute(db_path: str, spec: dict, *, client: GitHubClient | None = None) -> dict:
    """Fail-closed approved execution; reread existing posts to avoid duplicate side effect."""
    expected = packet(spec["repo"], spec["issue"], spec["message"])
    if spec != expected:
        raise ValueError("payload altered after preparation")
    api = client or GitHubCommentsAPI()
    with RealityStore(db_path) as store:
        if not store.is_approved(expected["transition_id"]):
            raise PermissionError("exact payload has no recorded approval")
        comments = api.comments(expected["repo"], expected["issue"])
        matches = [c for c in comments if isinstance(c.get("body"), str) and c["body"] == expected["message"] + "\n\n" + expected["marker"]]
        if len(matches) > 1:
            raise RuntimeError("multiple matching external comments; manual reconciliation required")
        if matches:
            confirmed = matches[0]
            outcome = "ALREADY_PRESENT"
        else:
            # The approval must precede the first post. A crash after post is recovered by reread.
            api.post(expected["repo"], expected["issue"], expected["message"] + "\n\n" + expected["marker"])
            outcome = "POSTED"
            verified = api.comments(expected["repo"], expected["issue"])
            matches = [c for c in verified if isinstance(c.get("body"), str) and c["body"] == expected["message"] + "\n\n" + expected["marker"]]
            if len(matches) != 1:
                raise RuntimeError("POST_UNVERIFIED: never settle or auto-retry blindly")
            confirmed = matches[0]
        locator = confirmed.get("html_url")
        if not isinstance(locator, str) or not locator.startswith(f"https://github.com/{expected['repo']}/issues/{expected['issue']}#"):
            raise RuntimeError("comment permalink missing/mismatched: not verified")
        if not isinstance(confirmed.get("id"), int):
            raise RuntimeError("comment ID unavailable: not verified")
        # Stable deterministic evidence/event IDs and transaction avoid duplicate logical settlement.
        identifier = expected["transition_id"]
        event_id = "evt_" + identifier
        evidence_id = "ev_" + identifier
        found = store.db.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone()
        if not found:
            actor = store.add_actor("github_comment_operator", actor_type="service", actor_id="actor_github_comments")
            obj = store.add_object(f"github:comment:{identifier}", "external_comment")
            if not store.db.execute("SELECT 1 FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone():
                store.add_evidence("external_receipt", locator, "exact approved comment found by fresh GitHub reread", evidence_id=evidence_id, metadata={"comment_id": confirmed["id"], "transition_id": identifier})
            store.record_event(actor_id=actor, object_id=obj, event_type="approved_comment_verified", resulting_state="EXPOSED", evidence_ids=[evidence_id], source=locator, event_id=event_id)
            store.settle(run_id=identifier, prior_state=None, action_taken="github.issue_comment", observed_result=locator, evidence_ids=[evidence_id], new_state="EXPOSED", next_transition=None, next_action=None, owner="human_operator")
        return {"status": "VERIFIED_" + outcome, "transition_id": identifier, "receipt": locator, "event_id": event_id}
