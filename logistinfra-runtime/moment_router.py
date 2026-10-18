#!/usr/bin/env python3
"""Moment Router v0: choose one dependency-correct action from persisted reality."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HARD_PREEMPT_ORDER = {
    "safety_security": 100,
    "external_actor_waiting": 90,
    "deadline_window": 80,
    "live_user_blocker": 70,
    "approved_time_sensitive": 60,
}

POSITIVE = (
    "external_consequence",
    "information_gain",
    "deadline_pressure",
    "dependency_unlock",
    "relationship_access_value",
    "proof_gain",
    "probability_now",
    "compounding_value",
)
NEGATIVE = (
    "switching_cost",
    "execution_cost",
    "reversibility_risk",
    "speculation_penalty",
)

@dataclass
class Decision:
    primary: dict[str, Any] | None
    interruption: dict[str, Any] | None
    suppressed: list[dict[str, Any]]
    waiting: list[dict[str, Any]]


def _score(item: dict[str, Any]) -> float:
    scores = item.get("scores", {})
    return sum(float(scores.get(k, 0)) for k in POSITIVE) - sum(float(scores.get(k, 0)) for k in NEGATIVE)


def _eligible(item: dict[str, Any], available_minutes: int) -> tuple[bool, str]:
    status = item.get("status", "active")
    if status in {"done", "cancelled", "rejected"}:
        return False, f"status={status}"
    if status == "waiting_external":
        return False, "waiting on external actor"
    if item.get("blocked", False):
        return False, "blocked"
    estimate = int(item.get("timebox_minutes", 0) or 0)
    if estimate and estimate > available_minutes and not item.get("splittable", False):
        return False, f"needs {estimate}m but only {available_minutes}m available"
    if not item.get("receipt_required"):
        return False, "missing receipt contract"
    if not item.get("operator"):
        return False, "missing operator"
    return True, "eligible"


def route(reality: dict[str, Any], available_minutes: int | None = None) -> Decision:
    available = int(available_minutes or reality.get("moment", {}).get("available_minutes", 60))
    candidates = reality.get("candidates", [])
    waiting = []
    eligible = []
    suppressed = []

    for item in candidates:
        if item.get("status") == "waiting_external":
            waiting.append({"item": item.get("action"), "next_check_at": item.get("next_check_at")})
        ok, reason = _eligible(item, available)
        if ok:
            item = dict(item)
            item["computed_score"] = _score(item)
            eligible.append(item)
        else:
            suppressed.append({"candidate": item.get("action"), "reason": reason})

    if not eligible:
        return Decision(None, None, suppressed, waiting)

    hard = [i for i in eligible if i.get("hard_gate") in HARD_PREEMPT_ORDER]
    if hard:
        hard.sort(key=lambda x: (HARD_PREEMPT_ORDER[x["hard_gate"]], x["computed_score"]), reverse=True)
        primary = hard[0]
    else:
        eligible.sort(key=lambda x: x["computed_score"], reverse=True)
        primary = eligible[0]

    for item in eligible:
        if item is not primary:
            suppressed.append({
                "candidate": item.get("action"),
                "reason": f"lower priority ({item['computed_score']:.1f} < {primary['computed_score']:.1f})",
            })

    interruption = reality.get("interruption_lane") or {
        "condition": "new external reply / security incident / deadline enters action window",
        "operator": "moment_router",
        "action": "recompute immediately",
    }
    return Decision(primary, interruption, suppressed, waiting)


def render(reality: dict[str, Any], decision: Decision, available_minutes: int) -> dict[str, Any]:
    p = decision.primary
    primary = None
    if p:
        primary = {
            "goal": p.get("goal"),
            "project": p.get("project"),
            "action": p.get("action"),
            "why_now": p.get("why_now"),
            "operator": p.get("operator"),
            "chat_reference": p.get("chat_reference"),
            "context_refs": p.get("context_refs", []),
            "first_physical_action": p.get("first_physical_action"),
            "stop_condition": p.get("stop_condition"),
            "receipt_required": p.get("receipt_required"),
            "timebox_minutes": p.get("timebox_minutes"),
            "score": p.get("computed_score"),
        }
    return {
        "moment": {
            "timestamp": reality.get("moment", {}).get("timestamp"),
            "available_minutes": available_minutes,
            "next_hard_commitment": reality.get("moment", {}).get("next_hard_commitment"),
        },
        "primary": primary,
        "interruption_lane": decision.interruption,
        "waiting": decision.waiting,
        "suppressed": decision.suppressed,
        "re_evaluate_when": [
            "primary completed/failed",
            "inbound external event",
            "deadline enters action window",
            "blocker clears",
            "calendar boundary reached",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="li-now", description="Return one highest-value action from current reality")
    parser.add_argument("reality", type=Path, help="JSON reality file")
    parser.add_argument("--available-minutes", type=int, default=None)
    args = parser.parse_args()

    reality = json.loads(args.reality.read_text(encoding="utf-8"))
    available = args.available_minutes or int(reality.get("moment", {}).get("available_minutes", 60))
    decision = route(reality, available)
    print(json.dumps(render(reality, decision, available), indent=2))


if __name__ == "__main__":
    main()
