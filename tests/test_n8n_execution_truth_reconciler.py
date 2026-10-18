from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).parents[1]
    / "proof"
    / "n8n"
    / "execution-truth-reconciler"
    / "analyzer.py"
)
spec = importlib.util.spec_from_file_location("execution_truth_reconciler", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

reconcile = module.reconcile_execution_truth


def test_running_execution_is_stale_when_owner_process_is_dead():
    result = reconcile({
        "id": "e1",
        "status": "running",
        "process_alive": False,
        "last_progress_at": "2026-09-10T22:10:00Z",
    })

    assert result["classification"] == "STALE_RUNNING_CONFIRMED"


def test_unfinished_execution_across_restart_is_stale_running():
    result = reconcile(
        {
            "id": "e2",
            "status": "running",
            "owner_process_started_at": "2026-09-10T20:00:00Z",
            "last_progress_at": "2026-09-10T22:15:00Z",
        },
        current_process_started_at="2026-09-10T22:21:50Z",
        unfinished_execution_ids={"e2"},
        now="2026-09-10T22:30:00Z",
    )

    assert result["classification"] == "STALE_RUNNING_CONFIRMED"
    assert result["unfinished_on_restart"] is True


def test_stale_progress_without_process_evidence_requires_reconciliation():
    result = reconcile(
        {
            "id": "e3",
            "status": "running",
            "last_progress_at": "2026-09-10T22:00:00Z",
        },
        now="2026-09-10T22:20:00Z",
        stale_after_seconds=300,
    )

    assert result["classification"] == "RUNNING_NEEDS_RECONCILIATION"


def test_running_state_is_not_disproven_without_negative_evidence():
    result = reconcile(
        {
            "id": "e4",
            "status": "running",
            "process_alive": True,
            "last_progress_at": "2026-09-10T22:19:30Z",
        },
        now="2026-09-10T22:20:00Z",
    )

    assert result["classification"] == "RUNNING_NOT_DISPROVEN"
