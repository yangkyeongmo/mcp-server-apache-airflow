"""Helpers for mapping MCP tools onto the vendored Airflow OpenAPI spec."""

from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml

from src.main import APITYPE_TO_FUNCTIONS

SPEC_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "airflow-openapi-v1-2.10.4.yaml"
SPEC_AIRFLOW_VERSION = "2.10.4"

# MCP-facing argument names that differ from the OpenAPI parameter / body field.
# Keys are tool names as registered with FastMCP.
TOOL_PARAM_ALIASES: dict[str, dict[str, str]] = {
    "get_connection": {"conn_id": "connection_id"},
    "update_connection": {"conn_id": "connection_id"},
    "delete_connection": {"conn_id": "connection_id"},
    "create_connection": {"conn_id": "connection_id"},
    "get_variable": {"key": "variable_key"},
    "update_variable": {"key": "variable_key"},
    "delete_variable": {"key": "variable_key"},
    "set_task_instances_state": {"state": "new_state", "task_ids": "task_id"},
    "update_task_instance": {"state": "new_state"},
}


@dataclass(frozen=True)
class ToolBinding:
    tool_name: str
    func: Callable[..., Any]
    api_attr: str
    method_name: str
    endpoint: Any


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    with SPEC_PATH.open(encoding="utf-8") as handle:
        spec = yaml.safe_load(handle)
    if not isinstance(spec, dict):
        raise TypeError(f"OpenAPI spec at {SPEC_PATH} is not a mapping")
    return spec


def resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Unsupported $ref: {ref}")
    node: Any = spec
    for part in ref[2:].split("/"):
        node = node[part]
    if not isinstance(node, dict):
        raise TypeError(f"$ref {ref} did not resolve to an object")
    return node


def resolve_schema(spec: dict[str, Any], schema: dict[str, Any] | None) -> dict[str, Any]:
    if not schema:
        return {"properties": {}}
    if "$ref" in schema:
        return resolve_schema(spec, resolve_ref(spec, schema["$ref"]))
    properties: dict[str, Any] = dict(schema.get("properties") or {})
    required: list[str] = list(schema.get("required") or [])
    for part in schema.get("allOf") or []:
        resolved = resolve_schema(spec, part)
        properties.update(resolved.get("properties") or {})
        required.extend(resolved.get("required") or [])
    merged = dict(schema)
    merged["properties"] = properties
    merged["required"] = required
    return merged


def operation_at(spec: dict[str, Any], path: str, method: str) -> dict[str, Any]:
    path_item = spec["paths"][path]
    return path_item[method.lower()]


def collect_parameters(spec: dict[str, Any], path: str, method: str) -> list[dict[str, Any]]:
    path_item = spec["paths"][path]
    operation = path_item[method.lower()]
    raw = list(path_item.get("parameters") or []) + list(operation.get("parameters") or [])
    params: list[dict[str, Any]] = []
    for param in raw:
        if "$ref" in param:
            param = resolve_ref(spec, param["$ref"])
        params.append(param)
    return params


def request_body_schema(spec: dict[str, Any], path: str, method: str) -> dict[str, Any] | None:
    operation = operation_at(spec, path, method)
    body = operation.get("requestBody")
    if not body:
        return None
    if "$ref" in body:
        body = resolve_ref(spec, body["$ref"])
    content = body.get("content") or {}
    json_body = content.get("application/json") or (next(iter(content.values())) if content else None)
    if not json_body:
        return None
    return resolve_schema(spec, json_body.get("schema") or {})


def allowed_field_names(spec: dict[str, Any], path: str, method: str) -> set[str]:
    names = {param["name"] for param in collect_parameters(spec, path, method)}
    body = request_body_schema(spec, path, method)
    if body:
        names.update((body.get("properties") or {}).keys())
    return names


def find_api_call(func: Callable[..., Any]) -> tuple[str, str]:
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)
    calls: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name):
            continue
        owner = node.func.value.id
        if owner.endswith("_api"):
            calls.append((owner, node.func.attr))
    if not calls:
        raise AssertionError(f"No *_api.* call found in {func.__name__}")
    return calls[-1]


def iter_tools() -> Iterator[ToolBinding]:
    for _api_type, getter in APITYPE_TO_FUNCTIONS.items():
        for func, name, _description, *_rest in getter():
            api_attr, method_name = find_api_call(func)
            module = inspect.getmodule(func)
            assert module is not None, f"No module for {name}"
            api_obj = getattr(module, api_attr)
            endpoint = getattr(api_obj, f"{method_name}_endpoint")
            yield ToolBinding(
                tool_name=name,
                func=func,
                api_attr=api_attr,
                method_name=method_name,
                endpoint=endpoint,
            )


def tool_param_names(func: Callable[..., Any]) -> list[str]:
    return list(inspect.signature(func).parameters)


def spec_name_for_param(tool_name: str, param: str) -> str:
    return TOOL_PARAM_ALIASES.get(tool_name, {}).get(param, param)
