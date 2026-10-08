from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ProvenanceFinding:
    tool_call_id: str
    tool_name: str | None
    observation: Any
    observation_empty: bool
    tool_data_present: bool
    tool_execution_index: int | None
    agent_execution_index: int | None
    ordering: str
    classification: str


def _empty_observation(value: Any) -> bool:
    # n8n issue #38870 reports the literal JSON string '""'.
    return value in ("", '""', None)


def _tool_payload_present(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    ai_tool = ((data.get("data") or {}).get("ai_tool"))
    if not ai_tool:
        return False
    for branch in ai_tool:
        if not branch:
            continue
        for item in branch:
            if isinstance(item, dict) and item.get("json") not in (None, {}, ""):
                return True
    return False


def _ordering(agent_execution_index: int | None, tool_execution_index: int | None) -> str:
    if agent_execution_index is None or tool_execution_index is None:
        return "UNKNOWN"
    if tool_execution_index < agent_execution_index:
        return "TOOL_BEFORE_AGENT"
    if tool_execution_index > agent_execution_index:
        return "AGENT_BEFORE_TOOL"
    return "SAME_INDEX"


def analyze_tool_observation_provenance(
    *,
    intermediate_steps: list[dict[str, Any]],
    action_responses: list[dict[str, Any]],
    agent_execution_index: int | None = None,
) -> list[dict[str, Any]]:
    """Correlate agent observations to engine tool responses by tool-call id.

    This deliberately does not infer the root cause. It distinguishes:
    - empty observation even though tool payload exists;
    - empty observation with no tool payload;
    - non-empty observation;
    - missing correlation record.
    """
    by_id: dict[str, dict[str, Any]] = {}
    for response in action_responses:
        action = response.get("action") or {}
        call_id = action.get("id") or (action.get("input") or {}).get("id")
        if isinstance(call_id, str) and call_id:
            by_id[call_id] = response

    findings: list[dict[str, Any]] = []

    for step in intermediate_steps:
        action = step.get("action") or {}
        call_id = action.get("toolCallId") or action.get("id")
        if not isinstance(call_id, str) or not call_id:
            findings.append(asdict(ProvenanceFinding(
                tool_call_id="UNAVAILABLE",
                tool_name=action.get("tool"),
                observation=step.get("observation"),
                observation_empty=_empty_observation(step.get("observation")),
                tool_data_present=False,
                tool_execution_index=None,
                agent_execution_index=agent_execution_index,
                ordering="UNKNOWN",
                classification="NO_TOOL_CALL_ID",
            )))
            continue

        response = by_id.get(call_id)
        observation = step.get("observation")
        empty = _empty_observation(observation)

        if response is None:
            classification = "MISSING_ACTION_RESPONSE"
            tool_present = False
            tool_index = None
        else:
            tool_data = response.get("data") or {}
            tool_present = _tool_payload_present(tool_data)
            tool_index = tool_data.get("executionIndex")
            if empty and tool_present:
                classification = "EMPTY_OBSERVATION_WITH_TOOL_DATA"
            elif empty and not tool_present:
                classification = "EMPTY_OBSERVATION_WITHOUT_TOOL_DATA"
            else:
                classification = "OBSERVATION_PRESENT"

        findings.append(asdict(ProvenanceFinding(
            tool_call_id=call_id,
            tool_name=action.get("tool"),
            observation=observation,
            observation_empty=empty,
            tool_data_present=tool_present,
            tool_execution_index=tool_index if isinstance(tool_index, int) else None,
            agent_execution_index=agent_execution_index,
            ordering=_ordering(agent_execution_index, tool_index if isinstance(tool_index, int) else None),
            classification=classification,
        )))

    return findings


def summarize(findings: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for item in findings:
        key = item["classification"]
        counts[key] = counts.get(key, 0) + 1

    strongest = "NO_ANOMALY"
    if counts.get("EMPTY_OBSERVATION_WITH_TOOL_DATA"):
        strongest = "BOUNDARY_MISMATCH"
    elif counts.get("EMPTY_OBSERVATION_WITHOUT_TOOL_DATA"):
        strongest = "UPSTREAM_OR_TIMING_GAP"
    elif counts.get("MISSING_ACTION_RESPONSE"):
        strongest = "CORRELATION_GAP"

    return {
        "total_steps": len(findings),
        "counts": counts,
        "strongest_signal": strongest,
        "claim_boundary": (
            "This analyzer localizes where evidence diverges. It does not prove the underlying "
            "race, scheduler, buffering, or serialization mechanism."
        ),
    }
