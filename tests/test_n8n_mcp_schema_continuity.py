from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).parents[1]
    / "proof"
    / "n8n"
    / "mcp-schema-continuity"
    / "analyzer.py"
)
spec = importlib.util.spec_from_file_location("mcp_schema_continuity", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

compare_tools_list = module.compare_tools_list
summarize = module.summarize


def tool(name, props):
    return {
        "name": name,
        "inputSchema": {
            "type": "object",
            **({"properties": props} if props is not None else {}),
        },
    }


def test_detects_full_schema_collapse():
    before = [
        tool("search_executions", {
            "status": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "number"},
        })
    ]
    after = [tool("search_executions", None)]

    findings = compare_tools_list(before, after)

    assert findings[0]["classification"] == "SCHEMA_COLLAPSED"
    assert findings[0]["typed_fields_lost"] == ["limit", "status"]
    assert summarize(findings)["strongest_signal"] == (
        "SERVER_OR_REGISTRY_SCHEMA_COLLAPSE_VISIBLE_IN_SNAPSHOT"
    )


def test_detects_partial_schema_drift_without_overcalling_full_collapse():
    before = [
        tool("update_workflow", {
            "nodes": {"type": "array"},
            "connections": {"type": "object"},
        })
    ]
    after = [
        tool("update_workflow", {
            "nodes": {"type": "string"},
            "connections": {"type": "object"},
        })
    ]

    findings = compare_tools_list(before, after)

    assert findings[0]["classification"] == "SCHEMA_CHANGED"
    assert findings[0]["typed_fields_lost"] == []
    assert summarize(findings)["strongest_signal"] == "SCHEMA_DRIFT_WITHOUT_FULL_COLLAPSE"


def test_unchanged_typed_schema_is_not_flagged():
    snapshot = [tool("search_executions", {"limit": {"type": "number"}})]
    findings = compare_tools_list(snapshot, snapshot)

    assert findings[0]["classification"] == "UNCHANGED"
    assert summarize(findings)["strongest_signal"] == "NO_SCHEMA_COLLAPSE_OBSERVED"


def test_recovery_is_distinct_from_collapse():
    before = [tool("search_executions", None)]
    after = [tool("search_executions", {"limit": {"type": "number"}})]

    findings = compare_tools_list(before, after)

    assert findings[0]["classification"] == "SCHEMA_RECOVERED"
