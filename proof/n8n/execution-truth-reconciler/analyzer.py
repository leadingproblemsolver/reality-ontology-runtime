from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


def _ts(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class ExecutionTruthFinding:
    execution_id: str
    ui_status: str
    process_alive: bool | None
    owner_process_started_at: str | None
    last_progress_at: str | None
    unfinished_on_restart: bool
    classification: str
    reason: str


def reconcile_execution_truth(
    execution: dict[str, Any],
    *,
    current_process_started_at: str | None = None,
    unfinished_execution_ids: set[str] | None = None,
    now: str | None = None,
    stale_after_seconds: int = 300,
) -> dict[str, Any]:
    """Classify whether a UI 'running' state is supported by process-level evidence.

    This is a diagnostic evidence model, not an n8n API integration.
    """
    execution_id = str(execution.get("id"))
    ui_status = str(execution.get("status") or "UNKNOWN").upper()
    owner_process_started_at = execution.get("owner_process_started_at")
    last_progress_at = execution.get("last_progress_at")
    process_alive = execution.get("process_alive")

    unfinished = execution_id in (unfinished_execution_ids or set())

    current_started = _ts(current_process_started_at)
    owner_started = _ts(owner_process_started_at)
    last_progress = _ts(last_progress_at)
    now_dt = _ts(now) or datetime.now(timezone.utc)

    if ui_status != "RUNNING":
        classification = "NON_RUNNING_STATE"
        reason = "UI does not claim the execution is currently running."
    elif process_alive is False:
        classification = "STALE_RUNNING_CONFIRMED"
        reason = "UI says RUNNING but the owning process is known dead."
    elif unfinished and current_started and owner_started and owner_started < current_started:
        classification = "STALE_RUNNING_CONFIRMED"
        reason = (
            "Execution was reported unfinished across a process restart; "
            "the UI RUNNING state belongs to an older process lifetime."
        )
    elif (
        ui_status == "RUNNING"
        and last_progress is not None
        and (now_dt - last_progress).total_seconds() > stale_after_seconds
        and process_alive is None
    ):
        classification = "RUNNING_NEEDS_RECONCILIATION"
        reason = (
            "UI says RUNNING but progress is stale and process ownership is unknown; "
            "fresh process-level verification is required."
        )
    else:
        classification = "RUNNING_NOT_DISPROVEN"
        reason = "No supplied evidence disproves the current RUNNING state."

    return asdict(
        ExecutionTruthFinding(
            execution_id=execution_id,
            ui_status=ui_status,
            process_alive=process_alive if isinstance(process_alive, bool) else None,
            owner_process_started_at=owner_process_started_at,
            last_progress_at=last_progress_at,
            unfinished_on_restart=unfinished,
            classification=classification,
            reason=reason,
        )
    )


def reconcile_many(
    executions: list[dict[str, Any]],
    **kwargs: Any,
) -> dict[str, Any]:
    findings = [reconcile_execution_truth(e, **kwargs) for e in executions]
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["classification"]] = counts.get(f["classification"], 0) + 1

    return {
        "findings": findings,
        "counts": counts,
        "claim_boundary": (
            "This reconciler compares declared execution state with supplied process/restart evidence. "
            "It does not diagnose the memory leak or prove how n8n should mutate execution status."
        ),
    }
