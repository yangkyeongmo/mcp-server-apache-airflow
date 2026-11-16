"""Helpers for comparing MCP tools against the vendored Airflow REST OpenAPI spec."""

from __future__ import annotations

import ast
import inspect
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from src.main import APITYPE_TO_FUNCTIONS

SPEC_PATH = Path(__file__).with_name("airflow-rest-v1-2.10.5.yaml")
SPEC_AIRFLOW_VERSION = "2.10.5"
SPEC_API_PREFIX = "/api/v1"

CLIENT_INTERNAL_PARAMS = {
    "async_req",
    "_host_index",
    "_preload_content",
    "_request_timeout",
    "_return_http_data_only",
    "_check_input_type",
    "_check_return_type",
    "_content_type",
    "_spec_property_naming",
}

API_OBJECT_NAMES = {
    "config_api",
    "connection_api",
    "dag_api",
    "dag_run_api",
    "dag_stats_api",
    "dataset_api",
    "event_log_api",
    "import_error_api",
    "monitoring_api",
    "plugin_api",
    "pool_api",
    "provider_api",
    "task_instance_api",
    "variable_api",
    "xcom_api",
}


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    with SPEC_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_ref(spec: dict[str, Any], obj: Any) -> Any:
    if isinstance(obj, dict) and "$ref" in obj:
        ref = obj["$ref"]
        if not ref.startswith("#/"):
            raise ValueError(f"Unsupported $ref: {ref}")
        node: Any = spec
        for part in ref[2:].split("/"):
            node = node[part]
        return resolve_ref(spec, node)
    return obj


def iter_registered_tools() -> Iterable[tuple[str, Callable[..., Any], str, bool]]:
    for api_type, getter in APITYPE_TO_FUNCTIONS.items():
        for func, name, _description, is_read_only in getter():
            yield api_type.value, func, name, is_read_only


def _is_api_call(node: ast.Call) -> bool:
    return (
        isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id in API_OBJECT_NAMES
    )


def find_api_calls(func: Callable[..., Any]) -> list[ast.Call]:
    tree = ast.parse(inspect.getsource(func))
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call) and _is_api_call(node)]


def client_endpoint_for_call(func: Callable[..., Any], call: ast.Call) -> Any:
    assert isinstance(call.func, ast.Attribute)
    assert isinstance(call.func.value, ast.Name)
    module = inspect.getmodule(func)
    if module is None:
        raise RuntimeError(f"Cannot resolve module for {func!r}")
    api_obj = getattr(module, call.func.value.id)
    endpoint = getattr(api_obj, f"{call.func.attr}_endpoint")
    return endpoint


def spec_operation(spec: dict[str, Any], path: str, method: str) -> dict[str, Any]:
    paths = spec.get("paths") or {}
    if path not in paths:
        raise AssertionError(f"OpenAPI spec has no path {path}")
    operation = paths[path].get(method.lower())
    if not operation:
        raise AssertionError(f"OpenAPI spec path {path} has no {method.upper()} operation")
    return operation


def operation_parameters(spec: dict[str, Any], path: str, method: str) -> list[dict[str, Any]]:
    path_item = spec["paths"][path]
    operation = spec_operation(spec, path, method)
    params: list[dict[str, Any]] = []
    for raw in list(path_item.get("parameters") or []) + list(operation.get("parameters") or []):
        params.append(resolve_ref(spec, raw))
    return params


def parameters_by_location(spec: dict[str, Any], path: str, method: str) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {"path": {}, "query": {}, "header": {}, "cookie": {}}
    for param in operation_parameters(spec, path, method):
        grouped.setdefault(param["in"], {})[param["name"]] = param
    return grouped


def schema_properties(spec: dict[str, Any], schema: dict[str, Any] | None) -> dict[str, Any]:
    if not schema:
        return {}
    schema = resolve_ref(spec, schema)
    properties: dict[str, Any] = {}
    if "allOf" in schema:
        for part in schema["allOf"]:
            properties.update(schema_properties(spec, part))
    properties.update(schema.get("properties") or {})
    return properties


def request_body_schema(spec: dict[str, Any], path: str, method: str) -> dict[str, Any] | None:
    operation = spec_operation(spec, path, method)
    raw_body = operation.get("requestBody")
    if not raw_body:
        return None
    body = resolve_ref(spec, raw_body)
    content = body.get("content") or {}
    for content_type in ("application/json", "application/json; charset=utf-8"):
        if content_type in content:
            return resolve_ref(spec, content[content_type].get("schema") or {})
    if content:
        first = next(iter(content.values()))
        return resolve_ref(spec, first.get("schema") or {})
    return None


def request_body_properties(spec: dict[str, Any], path: str, method: str) -> dict[str, Any]:
    return schema_properties(spec, request_body_schema(spec, path, method))


def _dict_literal_keys(node: ast.Dict) -> set[str]:
    keys: set[str] = set()
    for key in node.keys:
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            keys.add(key.value)
    return keys


def _assigned_subscript_keys(tree: ast.AST, name: str) -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(tree):
        target: ast.AST | None = None
        if isinstance(node, ast.Assign) and node.targets:
            target = node.targets[0]
        elif isinstance(node, ast.AnnAssign) and node.target is not None:
            target = node.target
        if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == name:
            slc = target.slice
            if isinstance(slc, ast.Constant) and isinstance(slc.value, str):
                keys.add(slc.value)
    return keys


def _name_bound_to_dict_keys(tree: ast.AST, name: str, seen: frozenset[str] | None = None) -> set[str]:
    keys: set[str] = set()
    already_seen: frozenset[str] = seen or frozenset()
    if name in already_seen:
        return keys
    already_seen = already_seen | {name}
    for node in ast.walk(tree):
        value: ast.AST | None = None
        target_names: list[str] = []
        if isinstance(node, ast.Assign):
            value = node.value
            target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            value = node.value
            target_names = [node.target.id]
        if name not in target_names or value is None:
            continue
        if isinstance(value, ast.Dict):
            keys.update(_dict_literal_keys(value))
        elif isinstance(value, ast.Call):
            for keyword in value.keywords:
                if keyword.arg:
                    keys.add(keyword.arg)
                elif isinstance(keyword.value, ast.Name):
                    keys.update(_name_bound_to_dict_keys(tree, keyword.value.id, already_seen))
    keys.update(_assigned_subscript_keys(tree, name))
    return keys


def payload_keys_for_call(func: Callable[..., Any], call: ast.Call) -> set[str]:
    """Return request field names the tool sends on this client call."""
    tree = ast.parse(inspect.getsource(func))
    keys: set[str] = set()

    def add_from_value(value: ast.AST) -> None:
        if isinstance(value, ast.Dict):
            keys.update(_dict_literal_keys(value))
        elif isinstance(value, ast.Name):
            keys.update(_name_bound_to_dict_keys(tree, value.id))
        elif isinstance(value, ast.Call):
            for keyword in value.keywords:
                if keyword.arg:
                    keys.add(keyword.arg)
                elif keyword.arg is None:
                    add_from_value(keyword.value)
            if isinstance(value.func, ast.Name) and value.func.id == "dict":
                pass

    for keyword in call.keywords:
        if keyword.arg in {None, "update_mask"}:
            if keyword.arg is None:
                add_from_value(keyword.value)
            continue
        if keyword.arg not in CLIENT_INTERNAL_PARAMS:
            # Direct kwargs are endpoint params (path/query/body), not schema fields.
            # Body models/dicts are expanded above.
            add_from_value(keyword.value)
    return keys


def python_type_to_openapi(annotation: Any) -> set[str]:
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())
    if annotation is inspect.Parameter.empty:
        return {"any"}
    if origin is None:
        mapping = {
            str: {"string"},
            int: {"integer"},
            float: {"number"},
            bool: {"boolean"},
            dict: {"object"},
            list: {"array"},
            type(None): {"null"},
        }
        if annotation in mapping:
            return mapping[annotation]
        name = getattr(annotation, "__name__", "")
        if name in {"datetime", "date"}:
            return {"string"}
        return {"any"}
    name = getattr(origin, "_name", None) or getattr(origin, "__name__", "") or str(origin)
    if name in {"Union", "UnionType"} or origin is type(int | str):
        types: set[str] = set()
        for arg in args:
            types.update(python_type_to_openapi(arg))
        return types
    if name in {"Optional"}:
        return python_type_to_openapi(args[0]) | {"null"}
    if name in {"List", "list", "Sequence"}:
        return {"array"}
    if name in {"Dict", "dict", "Mapping"}:
        return {"object"}
    return {"any"}


def openapi_schema_types(schema: dict[str, Any] | None) -> set[str]:
    if not schema:
        return {"any"}
    if "type" in schema:
        if schema["type"] == "string" and schema.get("format") == "date-time":
            return {"string"}
        return {schema["type"]}
    if "allOf" in schema:
        types: set[str] = set()
        for part in schema["allOf"]:
            types.update(openapi_schema_types(part))
        return types or {"any"}
    if "anyOf" in schema or "oneOf" in schema:
        types = set()
        for part in schema.get("anyOf") or schema.get("oneOf") or []:
            types.update(openapi_schema_types(part))
        return types or {"any"}
    return {"any"}


def types_are_compatible(python_types: set[str], spec_types: set[str]) -> bool:
    if "any" in python_types or "any" in spec_types:
        return True
    comparable = python_types - {"null"}
    if not comparable:
        return True
    if comparable & spec_types:
        return True
    if "integer" in comparable and "number" in spec_types:
        return True
    if "number" in comparable and "integer" in spec_types:
        return True
    # Airflow often types multi/comma-separated query params as string.
    if "array" in comparable and "string" in spec_types:
        return True
    if "string" in comparable and "array" in spec_types:
        return True
    return False
