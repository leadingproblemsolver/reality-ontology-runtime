from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = ROOT / "examples" / "logistinfra_mve_gateofai.json"


def run_cli(db: Path, *args: str) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "reality_ontology.cli", "--db", str(db), *args],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def test_gateofai_mission_survives_fresh_process_and_compiles_same_transition(tmp_path):
    """Acceptance proof: no chat/session memory is required to resume the live workload."""
    db = tmp_path / "reality.db"

    started = run_cli(db, "next-start", "--spec", str(SPEC))
    mission_id = started["mission_id"]
    selected = started["next_move"]
    expected_receipt = started["expected_receipt"]

    # Each call below is a brand-new Python process reading only the persisted runtime.
    resumed = run_cli(db, "resume")
    block = run_cli(db, "block", "--minutes", "25")
    events = run_cli(db, "next-events", mission_id)

    assert resumed["mission_id"] == mission_id
    assert resumed["status"] == "ACTIVE"
    assert resumed["selected_transition"] == selected
    assert resumed["expected_receipt"] == expected_receipt

    assert block["mission_id"] == mission_id
    assert block["exact_action"] == selected
    assert block["expected_receipt"] == expected_receipt
    assert block["timebox_minutes"] == 25
    assert block["preproof"]["required_receipt"] == expected_receipt

    event_types = [event["event_type"] for event in events]
    assert event_types == ["MISSION_STARTED", "CANDIDATE_SELECTED"]


def test_gateofai_fresh_process_refuses_invisible_continuation_after_timebox(tmp_path):
    """The restart path must force settlement once the persisted mission expires."""
    db = tmp_path / "reality.db"
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["timebox_seconds"] = 60
    short_spec = tmp_path / "short_gateofai.json"
    short_spec.write_text(json.dumps(spec), encoding="utf-8")

    started = run_cli(db, "next-start", "--spec", str(short_spec))
    assert started["status"] == "ACTIVE"

    # Move the persisted start timestamp backwards instead of sleeping.
    import sqlite3
    from datetime import datetime, timedelta, timezone

    with sqlite3.connect(db) as conn:
        old = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        conn.execute(
            "UPDATE next_missions SET started_at=? WHERE mission_id=?",
            (old, started["mission_id"]),
        )
        conn.commit()

    resumed = run_cli(db, "resume")
    assert resumed["status"] == "EXPIRED_NEEDS_SETTLEMENT"
    assert resumed["next_action"] == "SETTLE CURRENT MISSION BEFORE CONTINUING"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "reality_ontology.cli",
            "--db",
            str(db),
            "block",
            "--minutes",
            "10",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "cannot compile block while mission status is EXPIRED_NEEDS_SETTLEMENT" in (
        proc.stdout + proc.stderr
    )
