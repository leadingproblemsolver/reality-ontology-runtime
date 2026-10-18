from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).parents[1]
    / "proof"
    / "n8n"
    / "tool-observation-provenance"
    / "analyzer.py"
)
spec = importlib.util.spec_from_file_location("tool_observation_provenance", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

analyze = module.analyze_tool_observation_provenance
summarize = module.summarize


def action_response(call_id: str, execution_index: int, payload):
    return {
        "action": {
            "id": call_id,
            "nodeName": "Pricing Tool",
            "input": {"id": call_id, "query": "price"},
        },
        "data": {
            "data": {"ai_tool": [[{"json": payload}]]},
            "executionIndex": execution_index,
        },
    }


def step(call_id: str, observation):
    return {
        "action": {
            "tool": "get_pricing_info",
            "toolCallId": call_id,
        },
        "observation": observation,
    }


def test_flags_empty_observation_when_correlated_tool_payload_exists():
    findings = analyze(
        intermediate_steps=[step("call_1", '""')],
        action_responses=[action_response("call_1", 7, {"precio": 100})],
        agent_execution_index=9,
    )

    assert findings[0]["classification"] == "EMPTY_OBSERVATION_WITH_TOOL_DATA"
    assert findings[0]["ordering"] == "TOOL_BEFORE_AGENT"
    assert summarize(findings)["strongest_signal"] == "BOUNDARY_MISMATCH"


def test_distinguishes_empty_observation_when_tool_payload_is_missing():
    response = action_response("call_2", 10, {})
    response["data"]["data"]["ai_tool"] = []
    findings = analyze(
        intermediate_steps=[step("call_2", '""')],
        action_responses=[response],
        agent_execution_index=8,
    )

    assert findings[0]["classification"] == "EMPTY_OBSERVATION_WITHOUT_TOOL_DATA"
    assert findings[0]["ordering"] == "AGENT_BEFORE_TOOL"
    assert summarize(findings)["strongest_signal"] == "UPSTREAM_OR_TIMING_GAP"


def test_non_empty_observation_is_not_flagged():
    findings = analyze(
        intermediate_steps=[step("call_3", '[{"precio":100}]')],
        action_responses=[action_response("call_3", 4, {"precio": 100})],
        agent_execution_index=6,
    )

    assert findings[0]["classification"] == "OBSERVATION_PRESENT"
    assert summarize(findings)["strongest_signal"] == "NO_ANOMALY"


def test_missing_action_response_is_a_correlation_gap_not_proof_of_data_loss():
    findings = analyze(
        intermediate_steps=[step("call_missing", '""')],
        action_responses=[],
        agent_execution_index=5,
    )

    assert findings[0]["classification"] == "MISSING_ACTION_RESPONSE"
    assert summarize(findings)["strongest_signal"] == "CORRELATION_GAP"
