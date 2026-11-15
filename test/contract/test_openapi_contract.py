"""Contract tests: MCP tools vs Airflow 2.10 stable REST OpenAPI spec.

The vendored spec is Apache Airflow 2.10.4 (`/api/v1`). Tools go through
`apache-airflow-client` 2.x, which is generated from that API. Airflow 3 / v2
is out of scope until the client pin `>=2.7.0,<3` is lifted.
"""

from __future__ import annotations

import pytest

from test.contract.helpers import (
    SPEC_AIRFLOW_VERSION,
    SPEC_PATH,
    ToolBinding,
    allowed_field_names,
    collect_parameters,
    iter_tools,
    load_spec,
    operation_at,
    request_body_schema,
    spec_name_for_param,
    tool_param_names,
)

TOOLS = list(iter_tools())


@pytest.fixture(scope="module")
def spec() -> dict:
    return load_spec()


def test_vendored_spec_is_airflow_stable_v1(spec: dict) -> None:
    assert SPEC_PATH.is_file()
    assert spec["openapi"].startswith("3.")
    assert spec["info"]["version"] == SPEC_AIRFLOW_VERSION
    assert spec["servers"][0]["url"] == "/api/v1"
    assert "/dags" in spec["paths"]
    assert "/health" in spec["paths"]


def test_every_registered_tool_is_bound() -> None:
    names = [tool.tool_name for tool in TOOLS]
    assert names, "No tools discovered from APITYPE_TO_FUNCTIONS"
    assert len(names) == len(set(names)), f"Duplicate tool names: {names}"


@pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t.tool_name)
def test_tool_path_method_and_operation_id_match_spec(spec: dict, tool: ToolBinding) -> None:
    settings = tool.endpoint.settings
    path = settings["endpoint_path"]
    method = settings["http_method"]
    operation_id = settings["operation_id"]

    assert path in spec["paths"], f"{tool.tool_name}: path {path} missing from OpenAPI spec"
    path_item = spec["paths"][path]
    assert method.lower() in path_item, f"{tool.tool_name}: {method} {path} missing from OpenAPI spec"

    operation = operation_at(spec, path, method)
    assert operation["operationId"] == operation_id, (
        f"{tool.tool_name}: client operationId {operation_id!r} != spec {operation['operationId']!r}"
    )


@pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t.tool_name)
def test_tool_params_match_spec_path_query_or_body(spec: dict, tool: ToolBinding) -> None:
    settings = tool.endpoint.settings
    path = settings["endpoint_path"]
    method = settings["http_method"]
    allowed = allowed_field_names(spec, path, method)
    params = tool_param_names(tool.func)
    if not params:
        return

    unknown: list[str] = []
    for param in params:
        spec_name = spec_name_for_param(tool.tool_name, param)
        if spec_name not in allowed:
            unknown.append(f"{param} (mapped to {spec_name})")

    assert allowed, f"{tool.tool_name}: OpenAPI {method} {path} has no fields but the tool takes {params}"
    assert not unknown, f"{tool.tool_name} parameters not in {method} {path} spec fields {sorted(allowed)}: {unknown}"


@pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t.tool_name)
def test_required_path_params_are_tool_arguments(spec: dict, tool: ToolBinding) -> None:
    settings = tool.endpoint.settings
    params = collect_parameters(spec, settings["endpoint_path"], settings["http_method"])
    required_path = {p["name"] for p in params if p.get("in") == "path" and p.get("required", False)}
    aliases = {spec_name_for_param(tool.tool_name, name): name for name in tool_param_names(tool.func)}
    tool_spec_names = set(aliases) | set(tool_param_names(tool.func))
    missing = sorted(name for name in required_path if name not in tool_spec_names)
    assert not missing, f"{tool.tool_name} is missing required path params {missing}"


@pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t.tool_name)
def test_client_body_schema_matches_openapi(spec: dict, tool: ToolBinding) -> None:
    location_map = tool.endpoint.location_map
    body_params = [name for name, location in location_map.items() if location == "body"]
    spec_body = request_body_schema(
        spec,
        tool.endpoint.settings["endpoint_path"],
        tool.endpoint.settings["http_method"],
    )

    if not body_params:
        assert spec_body is None or not spec_body.get("properties"), (
            f"{tool.tool_name}: OpenAPI has a request body but the client endpoint does not"
        )
        return

    assert spec_body is not None, f"{tool.tool_name}: client sends a body but OpenAPI has none"
    spec_props = set((spec_body.get("properties") or {}).keys())
    assert spec_props, f"{tool.tool_name}: OpenAPI request body has no properties"

    openapi_types = tool.endpoint.openapi_types
    for body_param in body_params:
        model_types = openapi_types.get(body_param)
        if not model_types:
            continue
        model = model_types[0]
        model_fields = set(getattr(model, "attribute_map", {}) or {})
        if not model_fields:
            # Raw dict / untyped body (e.g. some request wrappers).
            continue
        missing_on_spec = sorted(field for field in model_fields if field not in spec_props)
        assert not missing_on_spec, (
            f"{tool.tool_name}: client model {model.__name__} fields {missing_on_spec} "
            f"are not in OpenAPI body properties {sorted(spec_props)}"
        )
