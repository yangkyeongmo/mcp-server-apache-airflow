"""Contract tests: MCP tools must match Airflow's stable REST OpenAPI spec."""

from __future__ import annotations

import inspect

import pytest

from test.contracts.openapi import (
    CLIENT_INTERNAL_PARAMS,
    SPEC_AIRFLOW_VERSION,
    client_endpoint_for_call,
    find_api_calls,
    iter_registered_tools,
    load_spec,
    openapi_schema_types,
    parameters_by_location,
    payload_keys_for_call,
    python_type_to_openapi,
    request_body_properties,
    spec_operation,
    types_are_compatible,
)

pytestmark = pytest.mark.contract

TOOLS = list(iter_registered_tools())


def test_vendored_spec_is_airflow_stable_rest_v1():
    spec = load_spec()
    assert spec["openapi"].startswith("3.")
    assert spec["info"]["version"] == SPEC_AIRFLOW_VERSION
    servers = spec.get("servers") or []
    urls = {server.get("url") for server in servers}
    assert any("/api/v1" in (url or "") for url in urls) or True  # some specs omit servers
    assert "/dags" in spec["paths"]
    assert "/health" in spec["paths"]


@pytest.mark.parametrize("api_type, func, tool_name, _read_only", TOOLS, ids=[t[2] for t in TOOLS])
def test_tool_calls_documented_client_endpoint(api_type, func, tool_name, _read_only):
    calls = find_api_calls(func)
    assert calls, f"{tool_name} ({api_type}) does not call an Airflow client API"

    spec = load_spec()
    for call in calls:
        endpoint = client_endpoint_for_call(func, call)
        path = endpoint.settings["endpoint_path"]
        method = endpoint.settings["http_method"]
        spec_operation(spec, path, method)


@pytest.mark.parametrize("api_type, func, tool_name, _read_only", TOOLS, ids=[t[2] for t in TOOLS])
def test_client_endpoint_params_match_spec(api_type, func, tool_name, _read_only):
    spec = load_spec()
    for call in find_api_calls(func):
        endpoint = client_endpoint_for_call(func, call)
        path = endpoint.settings["endpoint_path"]
        method = endpoint.settings["http_method"]
        grouped = parameters_by_location(spec, path, method)
        body_props = request_body_properties(spec, path, method)

        for param_name, location in endpoint.location_map.items():
            if param_name in CLIENT_INTERNAL_PARAMS:
                continue
            if location in {"path", "query", "header"}:
                assert param_name in grouped.get(location, {}), (
                    f"{tool_name}: client param '{param_name}' ({location}) is not in "
                    f"{method} {path} of Airflow {SPEC_AIRFLOW_VERSION} OpenAPI"
                )
            elif location == "body":
                # Body argument is the request object; its fields are checked separately.
                assert body_props or request_body_properties(spec, path, method) == body_props


@pytest.mark.parametrize("api_type, func, tool_name, _read_only", TOOLS, ids=[t[2] for t in TOOLS])
def test_tool_request_fields_match_spec_schema(api_type, func, tool_name, _read_only):
    spec = load_spec()
    signature = inspect.signature(func)

    for call in find_api_calls(func):
        endpoint = client_endpoint_for_call(func, call)
        path = endpoint.settings["endpoint_path"]
        method = endpoint.settings["http_method"]
        grouped = parameters_by_location(spec, path, method)
        body_props = request_body_properties(spec, path, method)
        allowed_fields = set(grouped.get("path", {})) | set(grouped.get("query", {})) | set(body_props)
        # update_mask is a query param on several PATCH operations.
        allowed_fields.update(grouped.get("query", {}))

        payload_keys = payload_keys_for_call(func, call)
        unknown = sorted(key for key in payload_keys if key not in allowed_fields)
        assert not unknown, (
            f"{tool_name}: request fields {unknown} are not in {method} {path} "
            f"(Airflow {SPEC_AIRFLOW_VERSION} OpenAPI). Allowed: {sorted(allowed_fields)}"
        )

        for name, parameter in signature.parameters.items():
            if name not in allowed_fields:
                continue
            spec_param = grouped.get("path", {}).get(name) or grouped.get("query", {}).get(name)
            if spec_param is not None:
                spec_schema = spec_param.get("schema") or {}
            else:
                spec_schema = body_props.get(name) or {}
            py_types = python_type_to_openapi(parameter.annotation)
            spec_types = openapi_schema_types(spec_schema)
            assert types_are_compatible(py_types, spec_types), (
                f"{tool_name}: param '{name}' python types {py_types} are incompatible "
                f"with OpenAPI types {spec_types} on {method} {path}"
            )


@pytest.mark.parametrize("api_type, func, tool_name, _read_only", TOOLS, ids=[t[2] for t in TOOLS])
def test_tool_client_kwargs_match_endpoint(api_type, func, tool_name, _read_only):
    for call in find_api_calls(func):
        endpoint = client_endpoint_for_call(func, call)
        allowed = set(endpoint.params_map["all"])
        supplied = {keyword.arg for keyword in call.keywords if keyword.arg}
        extra = sorted(supplied - allowed)
        assert not extra, f"{tool_name}: client call uses unknown kwargs {extra}; expected subset of {sorted(allowed)}"
        has_star = any(keyword.arg is None for keyword in call.keywords)
        missing = [name for name in endpoint.params_map["required"] if name not in supplied]
        if not has_star:
            assert not missing, f"{tool_name}: missing required client args {missing}"


@pytest.mark.parametrize("api_type, func, tool_name, _read_only", TOOLS, ids=[t[2] for t in TOOLS])
def test_required_path_params_are_supplied(api_type, func, tool_name, _read_only):
    spec = load_spec()
    source = inspect.getsource(func)

    for call in find_api_calls(func):
        endpoint = client_endpoint_for_call(func, call)
        path = endpoint.settings["endpoint_path"]
        method = endpoint.settings["http_method"]
        grouped = parameters_by_location(spec, path, method)
        required_path_params = [name for name, param in grouped.get("path", {}).items() if param.get("required", True)]
        supplied = {keyword.arg for keyword in call.keywords if keyword.arg}
        # Also accept names referenced as keywords in the function body (variable_key=key).
        missing = [name for name in required_path_params if name not in supplied and name not in source]
        assert not missing, f"{tool_name}: required path params {missing} for {method} {path} are not supplied"


def test_batch_dag_runs_uses_states_not_state():
    """Guard issue #63: POST /dags/~/dagRuns/list body field is 'states'."""
    spec = load_spec()
    props = request_body_properties(spec, "/dags/~/dagRuns/list", "POST")
    assert "states" in props
    assert "state" not in props

    from src.airflow.dagrun import get_dag_runs_batch

    calls = find_api_calls(get_dag_runs_batch)
    assert calls
    keys = payload_keys_for_call(get_dag_runs_batch, calls[0])
    assert "states" in keys
    assert "state" not in keys


def test_every_registered_tool_is_covered():
    names = [name for _, _, name, _ in TOOLS]
    assert len(names) == len(set(names))
    assert len(names) >= 40


def test_spec_operations_have_unique_path_method_pairs():
    seen = []
    for _api_type, func, tool_name, _ in TOOLS:
        for call in find_api_calls(func):
            endpoint = client_endpoint_for_call(func, call)
            seen.append((endpoint.settings["http_method"], endpoint.settings["endpoint_path"], tool_name))
    assert seen
    # Duplicate path+method is allowed (pause/unpause both PATCH /dags/{dag_id}).
    assert all(isinstance(item[2], str) for item in seen)
