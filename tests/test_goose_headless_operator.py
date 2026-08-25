from __future__ import annotations

from pathlib import Path

import pytest

from reality_ontology.executor import ApprovalRequired, ExecutionEngine
from reality_ontology.models import RiskLevel, TransitionContract
from reality_ontology.operators import GooseHeadlessOperator
from reality_ontology.store import RealityStore


def _fake_goose(tmp_path: Path) -> Path:
    binary = tmp_path / "goose"
    binary.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, sys\n"
        "target = pathlib.Path(os.environ['FAKE_GOOSE_TARGET'])\n"
        "target.write_text('GOOSE_EXECUTED\\n', encoding='utf-8')\n"
        "print('fake goose executed', ' '.join(sys.argv[1:]))\n",
        encoding="utf-8",
    )
    binary.chmod(0o755)
    return binary


def test_goose_headless_executes_then_rereads_before_settlement(tmp_path):
    fake = _fake_goose(tmp_path)
    target = tmp_path / "receipt.txt"
    db = tmp_path / "reality.db"

    with RealityStore(db) as store:
        actor = store.add_actor("operator")
        goal = store.add_goal("verified goose task", "fresh file reread")
        obj = store.add_object("workspace:goose-smoke", "workspace")
        seed = store.add_evidence("observation", "local://workspace", "workspace ready")
        store.record_event(
            actor_id=actor,
            object_id=obj,
            goal_id=goal,
            event_type="workspace_observed",
            resulting_state="READY",
            evidence_ids=[seed],
        )

        contract = TransitionContract(
            transition_id="goose-smoke-1",
            object_id=obj,
            goal_id=goal,
            entry_state="READY",
            desired_state="GOOSE_VERIFIED",
            operator="goose.headless",
            operation="execute_goal",
            proof_required="fresh file reread",
            risk=RiskLevel.L2_EXTERNAL_CONSEQUENTIAL,
        )
        engine = ExecutionEngine(store, [GooseHeadlessOperator(binary=str(fake))])
        inputs = {
            "task": "Create the requested receipt in the workspace",
            "cwd": str(tmp_path),
            "env": {"FAKE_GOOSE_TARGET": str(target)},
            "verification": {"type": "file_contains", "path": "receipt.txt", "contains": "GOOSE_EXECUTED"},
        }

        with pytest.raises(ApprovalRequired):
            engine.execute(contract, inputs=inputs, actor_id=actor)

        store.approve(contract.transition_id, actor)
        result = engine.execute(contract, inputs=inputs, actor_id=actor)

        assert store.current_state(obj) == "GOOSE_VERIFIED"
        attempt = store.attempt(result["attempt_id"])
        assert attempt["status"] == "SETTLED"
        assert attempt["external_side_effect"] == 1


def test_goose_timeout_still_reconciles_external_state(tmp_path):
    binary = tmp_path / "goose"
    target = tmp_path / "receipt.txt"
    binary.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, time\n"
        "pathlib.Path(os.environ['FAKE_GOOSE_TARGET']).write_text('SIDE_EFFECT_HAPPENED\\n', encoding='utf-8')\n"
        "time.sleep(5)\n",
        encoding="utf-8",
    )
    binary.chmod(0o755)

    op = GooseHeadlessOperator(binary=str(binary))
    contract = TransitionContract(
        transition_id="timeout",
        object_id="obj",
        goal_id=None,
        entry_state=None,
        desired_state="VERIFIED",
        operator="goose.headless",
        operation="execute_goal",
        proof_required="fresh reread",
        risk=RiskLevel.L2_EXTERNAL_CONSEQUENTIAL,
    )
    prepared = op.prepare(
        contract,
        {
            "task": "write then stall",
            "cwd": str(tmp_path),
            "timeout_seconds": 1.0,
            "env": {"FAKE_GOOSE_TARGET": str(target)},
            "verification": {"type": "file_contains", "path": "receipt.txt", "contains": "SIDE_EFFECT_HAPPENED"},
        },
    )
    execution = op.execute(contract, prepared)
    assert execution.result["timed_out"] is True
    assert execution.side_effect_possible is True
    verification = op.verify(contract, execution)
    assert verification.verified is True
    assert verification.metadata["goose_timed_out"] is True


def test_verification_path_cannot_escape_workspace(tmp_path):
    op = GooseHeadlessOperator(binary="goose")
    contract = TransitionContract(
        transition_id="scope",
        object_id="obj",
        goal_id=None,
        entry_state=None,
        desired_state="VERIFIED",
        operator="goose.headless",
        operation="execute_goal",
        proof_required="fresh reread",
        risk=RiskLevel.L2_EXTERNAL_CONSEQUENTIAL,
    )
    prepared = op.prepare(
        contract,
        {
            "task": "noop",
            "cwd": str(tmp_path),
            "verification": {"type": "file_contains", "path": "../outside.txt", "contains": "x"},
        },
    )
    from reality_ontology.models import OperatorResult
    with pytest.raises(ValueError, match="escapes configured cwd"):
        op.verify(contract, OperatorResult({"cwd": prepared["cwd"], "verification": prepared["verification"]}, True))
