"""MCP tools/list compatibility: snapshot freshness and breaking-change rules."""

from __future__ import annotations

import copy

import pytest

from test.mcp.compat import (
    BREAKING_NEW_REQUIRED,
    BREAKING_REMOVED_PARAM,
    BREAKING_REMOVED_TOOL,
    BREAKING_TYPE_CHANGE,
    SNAPSHOT_PATH,
    compatibility_diff,
    dump_from_list_tools,
    load_snapshot,
    snapshot_matches,
)
from test.mcp.stdio import mcp_stdio_session, parse_client_text


def _tool(name: str, properties: dict, required: list[str] | None = None) -> dict:
    schema: dict = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return {"name": name, "inputSchema": schema}


def _dump(*tools: dict) -> dict:
    return {"protocol": "mcp-tools/list", "tools": {tool["name"]: tool for tool in tools}}


def test_compat_allows_new_tools_and_optional_params():
    baseline = _dump(
        _tool("get_health", {}, []),
        _tool("get_variable", {"key": {"type": "string"}}, ["key"]),
    )
    current = _dump(
        _tool("get_health", {}, []),
        _tool(
            "get_variable",
            {"key": {"type": "string"}, "include_description": {"type": "boolean"}},
            ["key"],
        ),
        _tool("new_tool", {"id": {"type": "string"}}, ["id"]),
    )
    assert compatibility_diff(baseline, current) == []


def test_compat_fails_on_removed_tool_param_required_and_type():
    baseline = _dump(
        _tool(
            "create_variable",
            {
                "key": {"type": "string"},
                "value": {"type": "string"},
                "description": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            },
            ["key", "value"],
        ),
        _tool("legacy_tool", {"id": {"type": "string"}}, ["id"]),
    )
    current = _dump(
        _tool(
            "create_variable",
            {
                "key": {"type": "integer"},
                "description": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "ttl": {"type": "integer"},
            },
            ["key", "description", "ttl"],
        ),
    )
    kinds = {(item["kind"], item["tool"]) for item in compatibility_diff(baseline, current)}
    assert (BREAKING_REMOVED_TOOL, "legacy_tool") in kinds
    assert (BREAKING_REMOVED_PARAM, "create_variable") in kinds
    assert (BREAKING_NEW_REQUIRED, "create_variable") in kinds
    assert (BREAKING_TYPE_CHANGE, "create_variable") in kinds


def test_parse_client_text_handles_airflow_datetime_repr():
    payload = parse_client_text(
        "{'dags': [{'dag_id': 'example_bash_operator', "
        "'last_parsed_time': datetime.datetime(2026, 11, 15, 12, 31, 33, 346287, tzinfo=tzlocal())}], "
        "'total_entries': 74.0}"
    )
    assert payload["dags"][0]["dag_id"] == "example_bash_operator"
    assert payload["total_entries"] == 74.0


def test_snapshot_matches_identical_dumps():
    payload = _dump(_tool("get_health", {}))
    assert snapshot_matches(payload, copy.deepcopy(payload)) == []
    other = _dump(_tool("get_health", {"limit": {"type": "integer"}}))
    assert snapshot_matches(other, payload)


@pytest.mark.asyncio
async def test_live_stdio_dump_matches_committed_snapshot():
    async with mcp_stdio_session() as session:
        listed = await session.list_tools()
    current = dump_from_list_tools(listed.tools)
    assert current["tools"], "stdio tools/list returned no tools"
    errors = snapshot_matches(current, load_snapshot(SNAPSHOT_PATH))
    assert not errors, "\n".join(errors)
