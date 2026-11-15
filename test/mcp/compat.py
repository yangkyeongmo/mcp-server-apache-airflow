"""MCP tools/list snapshot format and compatibility diff."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SNAPSHOT_PATH = Path(__file__).with_name("tools_snapshot.json")

BREAKING_REMOVED_TOOL = "removed_or_renamed_tool"
BREAKING_REMOVED_PARAM = "removed_param"
BREAKING_NEW_REQUIRED = "newly_required_param"
BREAKING_TYPE_CHANGE = "param_type_change"


def dump_from_list_tools(tools: list[Any]) -> dict[str, Any]:
    """Normalize an MCP tools/list payload for snapshots and diffs."""
    entries: dict[str, Any] = {}
    for tool in tools:
        name = tool.name if hasattr(tool, "name") else tool["name"]
        schema = tool.inputSchema if hasattr(tool, "inputSchema") else tool["inputSchema"]
        entries[name] = {
            "name": name,
            "inputSchema": _jsonable(schema),
        }
    return {
        "protocol": "mcp-tools/list",
        "tools": dict(sorted(entries.items())),
    }


def load_snapshot(path: Path | str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_snapshot(payload: dict[str, Any], path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(serialized, encoding="utf-8")


def snapshot_matches(current: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    """Return mismatches between a live dump and the committed snapshot."""
    errors: list[str] = []
    current_tools = current.get("tools") or {}
    snapshot_tools = snapshot.get("tools") or {}
    if set(current_tools) != set(snapshot_tools):
        added = sorted(set(current_tools) - set(snapshot_tools))
        removed = sorted(set(snapshot_tools) - set(current_tools))
        if added:
            errors.append(f"snapshot missing tools (update the snapshot): {added}")
        if removed:
            errors.append(f"snapshot has extra tools (update the snapshot): {removed}")
    for name in sorted(set(current_tools) & set(snapshot_tools)):
        if current_tools[name].get("inputSchema") != snapshot_tools[name].get("inputSchema"):
            errors.append(f"{name}: inputSchema does not match committed snapshot (update the snapshot)")
    return errors


def compatibility_diff(baseline: dict[str, Any], current: dict[str, Any]) -> list[dict[str, str]]:
    """
    Compare two tools/list dumps.

    Breaking: removed/renamed tools, removed params, newly required params, param type changes.
    Allowed: new tools, new optional params.
    """
    findings: list[dict[str, str]] = []
    baseline_tools = baseline.get("tools") or {}
    current_tools = current.get("tools") or {}

    for name in sorted(set(baseline_tools) - set(current_tools)):
        findings.append(
            {
                "kind": BREAKING_REMOVED_TOOL,
                "tool": name,
                "detail": f"tool '{name}' is missing (removed or renamed)",
            }
        )

    for name in sorted(set(baseline_tools) & set(current_tools)):
        findings.extend(
            _diff_tool_schema(
                name,
                baseline_tools[name].get("inputSchema") or {},
                current_tools[name].get("inputSchema") or {},
            )
        )
    return findings


def _diff_tool_schema(tool: str, baseline: dict[str, Any], current: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    base_props = _properties(baseline)
    cur_props = _properties(current)
    base_required = set(_required(baseline))
    cur_required = set(_required(current))

    for param in sorted(set(base_props) - set(cur_props)):
        findings.append(
            {
                "kind": BREAKING_REMOVED_PARAM,
                "tool": tool,
                "detail": f"parameter '{param}' was removed",
            }
        )

    for param in sorted(cur_required - base_required):
        findings.append(
            {
                "kind": BREAKING_NEW_REQUIRED,
                "tool": tool,
                "detail": f"parameter '{param}' is now required",
            }
        )

    for param in sorted(set(base_props) & set(cur_props)):
        base_type = canonical_type(base_props[param])
        cur_type = canonical_type(cur_props[param])
        if base_type != cur_type:
            findings.append(
                {
                    "kind": BREAKING_TYPE_CHANGE,
                    "tool": tool,
                    "detail": f"parameter '{param}' type changed from {base_type!r} to {cur_type!r}",
                }
            )
    return findings


def _properties(schema: dict[str, Any]) -> dict[str, Any]:
    props = schema.get("properties")
    return props if isinstance(props, dict) else {}


def _required(schema: dict[str, Any]) -> list[str]:
    required = schema.get("required") or []
    return [item for item in required if isinstance(item, str)]


def canonical_type(schema: Any) -> Any:
    """Strip titles/descriptions/defaults so only wire types are compared."""
    if not isinstance(schema, dict):
        return schema
    if "anyOf" in schema:
        return {"anyOf": [canonical_type(item) for item in schema["anyOf"]]}
    if "oneOf" in schema:
        return {"oneOf": [canonical_type(item) for item in schema["oneOf"]]}
    if "allOf" in schema:
        return {"allOf": [canonical_type(item) for item in schema["allOf"]]}
    if "$ref" in schema:
        return {"$ref": schema["$ref"]}
    result: dict[str, Any] = {}
    if "type" in schema:
        result["type"] = schema["type"]
    if schema.get("type") == "array":
        result["items"] = canonical_type(schema.get("items", {}))
    if schema.get("type") == "object":
        result["properties"] = {key: canonical_type(value) for key, value in _properties(schema).items()}
        result["required"] = sorted(_required(schema))
    if "enum" in schema:
        result["enum"] = schema["enum"]
    if "format" in schema:
        result["format"] = schema["format"]
    return result


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def format_findings(findings: list[dict[str, str]]) -> str:
    if not findings:
        return "No breaking MCP tool schema changes."
    lines = ["Breaking MCP tool schema changes:"]
    for item in findings:
        lines.append(f"- [{item['kind']}] {item['tool']}: {item['detail']}")
    return "\n".join(lines)
