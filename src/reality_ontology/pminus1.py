from __future__ import annotations

import json
from typing import Any

from .nextmove import NextMoveEngine


def _latest_settlement(store: Any) -> dict[str, Any] | None:
    try:
        row = store.db.execute(
            "SELECT * FROM settlements ORDER BY settled_at DESC, rowid DESC LIMIT 1"
        ).fetchone()
    except Exception:
        return None
    if not row:
        return None
    data = dict(row)
    for key in ("evidence_ids_json", "unresolved_json", "waiting_external_json", "do_not_repeat_json"):
        if key in data and data[key] is not None:
            try:
                data[key[:-5] if key.endswith("_json") else key] = json.loads(data[key])
            except Exception:
                pass
    return data


def resume_view(store: Any) -> dict[str, Any]:
    """Return the smallest restart-safe execution packet available from durable state."""
    engine = NextMoveEngine(store)
    try:
        mission = engine.current()
    except KeyError:
        mission = None

    settlement = _latest_settlement(store)

    if mission is None:
        return {
            "status": "NO_MISSION",
            "target": None,
            "state": None,
            "last_settlement": settlement,
            "next_action": settlement.get("next_action") if settlement else None,
            "blockers": [],
            "waiting_external": settlement.get("waiting_external", []) if settlement else [],
            "wake_at": None,
            "restart_instruction": "Start one dependency-correct mission before doing more work.",
        }

    status = mission["status"]
    if status == "ACTIVE":
        next_action = mission["next_move"]
    elif status == "EXPIRED_NEEDS_SETTLEMENT":
        next_action = "SETTLE CURRENT MISSION BEFORE CONTINUING"
    else:
        next_action = (
            settlement.get("next_action")
            if settlement and settlement.get("next_action")
            else "Select the next dependency-correct transition."
        )

    blockers: list[str] = []
    if status == "EXPIRED_NEEDS_SETTLEMENT":
        blockers.append("Current mission timebox expired and requires explicit settlement.")
    if settlement:
        blockers.extend(settlement.get("unresolved", []) or [])

    return {
        "status": status,
        "mission_id": mission["mission_id"],
        "target": mission["target"],
        "state": mission["now"],
        "delta": mission["delta"],
        "selected_transition": mission["next_move"],
        "expected_postcondition": mission["expected_postcondition"],
        "expected_receipt": mission["expected_receipt"],
        "last_settlement": settlement,
        "next_action": next_action,
        "blockers": blockers,
        "waiting_external": settlement.get("waiting_external", []) if settlement else [],
        "wake_at": None,
        "owner": mission.get("owner"),
        "restart_instruction": (
            "Execute only the selected transition, capture an inspectable receipt, then settle."
            if status == "ACTIVE"
            else "Do not reconstruct chat history. Continue from the durable settlement/state above."
        ),
    }


def _phase_plan(minutes: int) -> list[dict[str, Any]]:
    if minutes == 10:
        return [
            {"phase": "SYNC", "start_minute": 0, "end_minute": 1},
            {"phase": "PREP", "start_minute": 1, "end_minute": 2},
            {"phase": "EXECUTE", "start_minute": 2, "end_minute": 7},
            {"phase": "VERIFY_SETTLE", "start_minute": 7, "end_minute": 9},
            {"phase": "RESTART_CUE", "start_minute": 9, "end_minute": 10},
        ]
    if minutes == 25:
        return [
            {"phase": "SYNC", "start_minute": 0, "end_minute": 1},
            {"phase": "PREP", "start_minute": 1, "end_minute": 4},
            {"phase": "EXECUTE", "start_minute": 4, "end_minute": 20},
            {"phase": "VERIFY_SETTLE", "start_minute": 20, "end_minute": 22},
            {"phase": "RESTART_CUE", "start_minute": 22, "end_minute": 25},
        ]
    raise ValueError("minutes must be 10 or 25 in the P-1 MVE")


def compile_block(store: Any, *, minutes: int = 25) -> dict[str, Any]:
    """Compile the active NextMove mission into one bounded CogniTime block."""
    resume = resume_view(store)
    if resume["status"] != "ACTIVE":
        raise ValueError(
            f"cannot compile block while mission status is {resume['status']}; "
            "settle/start a mission first"
        )

    mission_id = resume["mission_id"]
    receipt = resume["expected_receipt"]

    return {
        "block_id": f"block_{mission_id}_{minutes}m",
        "mission_id": mission_id,
        "timebox_minutes": minutes,
        "exact_action": resume["selected_transition"],
        "surface": "resolve from transition/capability at execution time",
        "inputs": [
            "durable mission state",
            "only source artifacts required by the selected transition",
        ],
        "phases": _phase_plan(minutes),
        "stop_condition": (
            "Stop when the expected receipt is inspectable, the transition is falsified, "
            "authority/prerequisites fail, or the timebox expires."
        ),
        "expected_postcondition": resume["expected_postcondition"],
        "expected_receipt": receipt,
        "fallback": "Settle BLOCKED or FALSIFIED_HYPOTHESIS; do not continue invisibly.",
        "restart_cue": f"ro next-events {mission_id} && ro resume",
        "preproof": {
            "claim_ceiling_before": "PREPARED",
            "claim_on_success": "The selected transition produced the stated inspectable receipt.",
            "required_receipt": receipt,
            "proof_surface": "durable mission events + receipt locator + settlement observation",
            "promotion_rule": "Claim strength must not exceed the strongest inspectable receipt.",
            "externalization_ready_when": (
                "A fresh process can reproduce the state transition and inspect the receipt "
                "without chat/session memory."
            ),
        },
    }
