from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ToolSchemaFinding:
    tool_name: str
    before_has_properties: bool
    after_has_properties: bool
    before_property_count: int
    after_property_count: int
    typed_fields_lost: list[str]
    classification: str


def _schema(tool: dict[str, Any]) -> dict[str, Any]:
    value = tool.get("inputSchema")
    if isinstance(value, dict):
        return value
    value = tool.get("parameters")
    if isinstance(value, dict):
        return value
    return {}


def _properties(tool: dict[str, Any]) -> dict[str, Any]:
    props = _schema(tool).get("properties")
    return props if isinstance(props, dict) else {}


def compare_tools_list(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Diff two MCP tools/list snapshots without guessing the cache/source bug."""
    before_map = {
        str(tool.get("name")): tool
        for tool in before
        if isinstance(tool, dict) and tool.get("name")
    }
    after_map = {
        str(tool.get("name")): tool
        for tool in after
        if isinstance(tool, dict) and tool.get("name")
    }

    findings: list[dict[str, Any]] = []

    for name in sorted(set(before_map) | set(after_map)):
        b = before_map.get(name)
        a = after_map.get(name)

        if b is None:
            classification = "TOOL_ADDED"
            b_props = {}
            a_props = _properties(a or {})
        elif a is None:
            classification = "TOOL_REMOVED"
            b_props = _properties(b)
            a_props = {}
        else:
            b_props = _properties(b)
            a_props = _properties(a)

            if b_props and not a_props:
                classification = "SCHEMA_COLLAPSED"
            elif not b_props and a_props:
                classification = "SCHEMA_RECOVERED"
            elif b_props != a_props:
                classification = "SCHEMA_CHANGED"
            else:
                classification = "UNCHANGED"

        lost = sorted(set(b_props) - set(a_props))

        findings.append(asdict(ToolSchemaFinding(
            tool_name=name,
            before_has_properties=bool(b_props),
            after_has_properties=bool(a_props),
            before_property_count=len(b_props),
            after_property_count=len(a_props),
            typed_fields_lost=lost,
            classification=classification,
        )))

    return findings


def summarize(findings: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    collapsed: list[str] = []
    for finding in findings:
        key = finding["classification"]
        counts[key] = counts.get(key, 0) + 1
        if key == "SCHEMA_COLLAPSED":
            collapsed.append(finding["tool_name"])

    if collapsed:
        strongest = "SERVER_OR_REGISTRY_SCHEMA_COLLAPSE_VISIBLE_IN_SNAPSHOT"
    elif counts.get("SCHEMA_CHANGED"):
        strongest = "SCHEMA_DRIFT_WITHOUT_FULL_COLLAPSE"
    else:
        strongest = "NO_SCHEMA_COLLAPSE_OBSERVED"

    return {
        "counts": counts,
        "collapsed_tools": collapsed,
        "strongest_signal": strongest,
        "claim_boundary": (
            "A tools/list snapshot diff can prove emitted schema drift. "
            "It cannot by itself identify whether generation, caching, registry state, "
            "or a client-side transformation caused that drift."
        ),
    }
