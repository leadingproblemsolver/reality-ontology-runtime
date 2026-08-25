from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from reality_ontology.executor import ExecutionEngine
from reality_ontology.models import RiskLevel, TransitionContract
from reality_ontology.operators import GooseHeadlessOperator
from reality_ontology.store import RealityStore


def _flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    marker = os.environ["REALITY_SMOKE_MARKER"]
    repository = os.environ["GITHUB_REPOSITORY"]
    receipt = Path(os.environ["REALITY_SMOKE_RECEIPT"]).resolve()
    safe_marker = re.sub(r"[^A-Za-z0-9_.-]+", "-", marker)
    db = root / ".runtime" / f"goose-mcp-smoke-{safe_marker}.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    if db.exists():
        db.unlink()
    if receipt.exists():
        receipt.unlink()

    timeout_seconds = float(os.environ.get("REALITY_GOOSE_TIMEOUT_SECONDS", "180"))
    expect_timeout = _flag("REALITY_EXPECT_GOOSE_TIMEOUT")
    expect_receipt = _flag("REALITY_EXPECT_LOCAL_RECEIPT", True)
    transition_id = f"goose-mcp-github:{marker}"

    with RealityStore(db) as store:
        actor = store.add_actor("github-actions", actor_type="automation")
        goal = store.add_goal("EXPOSED", "independent GitHub reread after Goose MCP mutation")
        obj = store.add_object(f"github-issue-probe:{marker}", "external_probe")
        seed = store.add_evidence("observation", "github-actions://workspace", "smoke workspace prepared")
        store.record_event(
            actor_id=actor,
            object_id=obj,
            goal_id=goal,
            event_type="smoke_prepared",
            resulting_state="PREPARED",
            evidence_ids=[seed],
        )
        approval_evidence = store.add_evidence(
            "decision",
            "github-actions://workflow-policy",
            "reversible issue creation approved for integration smoke",
        )
        store.approve(transition_id, actor, evidence_id=approval_evidence)

        contract = TransitionContract(
            transition_id=transition_id,
            object_id=obj,
            goal_id=goal,
            entry_state="PREPARED",
            desired_state="EXPOSED",
            operator="goose.headless",
            operation="github_mcp_probe_issue",
            proof_required="fresh GitHub API reread and unique-marker assertion",
            risk=RiskLevel.L2_EXTERNAL_CONSEQUENTIAL,
        )
        verifier = root / "scripts" / "verify_github_issue.py"
        result = ExecutionEngine(store, [GooseHeadlessOperator()]).execute(
            contract,
            inputs={
                "recipe": "examples/goose_github_mcp_smoke.yaml",
                "cwd": str(root),
                "timeout_seconds": timeout_seconds,
                "verification": {
                    "type": "command_exit",
                    "argv": [
                        sys.executable,
                        str(verifier),
                        "--receipt", str(receipt),
                        "--marker", marker,
                        "--repository", repository,
                    ],
                    "exit_code": 0,
                    "timeout_seconds": 60,
                },
            },
            actor_id=actor,
            owner="github-actions",
        )
        attempt = store.attempt(result["attempt_id"])
        execution_receipt = json.loads(attempt["result_json"] or "{}")
        timed_out = bool(execution_receipt.get("timed_out", False))
        local_receipt_present = receipt.is_file()
        assert timed_out is expect_timeout, (timed_out, expect_timeout, execution_receipt)
        assert local_receipt_present is expect_receipt, (local_receipt_present, expect_receipt)
        assert attempt["status"] == "SETTLED"
        assert store.current_state(obj) == "EXPOSED"

    with RealityStore(db) as fresh:
        assert fresh.current_state(obj) == "EXPOSED"
        packet = fresh.context_packet(goal)
        assert packet["objects"][0]["current_state"] == "EXPOSED"

    print(json.dumps({
        "marker": marker,
        "attempt_id": result["attempt_id"],
        "settlement_id": result["settlement_id"],
        "evidence_id": result["evidence_id"],
        "goose_timed_out": timed_out,
        "expected_timeout": expect_timeout,
        "local_transport_receipt_present": local_receipt_present,
        "expected_local_transport_receipt": expect_receipt,
        "state_after_fresh_restart": "EXPOSED",
        "reality_db": str(db),
        "transport_receipt": str(receipt),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
