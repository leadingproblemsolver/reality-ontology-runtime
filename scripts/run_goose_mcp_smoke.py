from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from reality_ontology.executor import ExecutionEngine
from reality_ontology.models import RiskLevel, TransitionContract
from reality_ontology.operators import GooseHeadlessOperator
from reality_ontology.store import RealityStore


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    marker = os.environ["REALITY_SMOKE_MARKER"]
    receipt = Path(os.environ["REALITY_SMOKE_RECEIPT"]).resolve()
    db = root / ".runtime" / "goose-mcp-smoke.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    if db.exists():
        db.unlink()
    if receipt.exists():
        receipt.unlink()

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
            proof_required="fresh GitHub API reread",
            risk=RiskLevel.L2_EXTERNAL_CONSEQUENTIAL,
        )
        verifier = root / "scripts" / "verify_github_issue.py"
        result = ExecutionEngine(store, [GooseHeadlessOperator()]).execute(
            contract,
            inputs={
                "recipe": "examples/goose_github_mcp_smoke.yaml",
                "cwd": str(root),
                "timeout_seconds": 180,
                "verification": {
                    "type": "command_exit",
                    "argv": [
                        sys.executable,
                        str(verifier),
                        "--receipt",
                        str(receipt),
                        "--marker",
                        marker,
                    ],
                    "exit_code": 0,
                    "timeout_seconds": 60,
                },
            },
            actor_id=actor,
            owner="github-actions",
        )
        attempt = store.attempt(result["attempt_id"])
        assert attempt["status"] == "SETTLED"
        assert store.current_state(obj) == "EXPOSED"

    with RealityStore(db) as fresh:
        assert fresh.current_state(obj) == "EXPOSED"
        packet = fresh.context_packet(goal)
        assert packet["objects"][0]["current_state"] == "EXPOSED"

    print(
        json.dumps(
            {
                "marker": marker,
                "attempt_id": result["attempt_id"],
                "settlement_id": result["settlement_id"],
                "evidence_id": result["evidence_id"],
                "state_after_fresh_restart": "EXPOSED",
                "reality_db": str(db),
                "transport_receipt": str(receipt),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
