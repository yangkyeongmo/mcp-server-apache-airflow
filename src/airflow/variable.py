import json
from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.variable_api import VariableApi

from src.airflow.airflow_client import api_client

variable_api = VariableApi(api_client)

# Airflow stores variable values as strings, but clients may deliver a JSON
# document as a structured value; accept every JSON type and stringify below.
JSONValue = Union[str, bool, int, float, List[Any], Dict[str, Any]]


def as_string(value: JSONValue) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (list_variables, "list_variables", "List all variables", True),
        (create_variable, "create_variable", "Create a variable", False),
        (get_variable, "get_variable", "Get a variable by key", True),
        (update_variable, "update_variable", "Update a variable by key", False),
        (delete_variable, "delete_variable", "Delete a variable by key", False),
    ]


async def list_variables(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by

    response = variable_api.get_variables(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def create_variable(
    key: str, value: JSONValue, description: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    variable_request: Dict[str, Any] = {
        "key": key,
        "value": as_string(value),
    }
    if description is not None:
        variable_request["description"] = description

    response = variable_api.post_variables(variable=variable_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_variable(key: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = variable_api.get_variable(variable_key=key)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def update_variable(
    key: str, value: Optional[JSONValue] = None, description: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    if value is None:
        # The v1 schema requires value and PATCH replaces it, so keep the current one
        # when only the description changes. update_mask cannot be used here: Airflow
        # loads value under the "val" attribute and rejects mask entries for it.
        value = variable_api.get_variable(variable_key=key).to_dict().get("value")

    update_request: Dict[str, Any] = {"key": key, "value": as_string(value)}
    if description is not None:
        update_request["description"] = description

    response = variable_api.patch_variable(variable_key=key, variable=update_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_variable(key: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = variable_api.delete_variable(variable_key=key)
    # a 204 response deserializes to None, so there is no body to dump
    result = response.to_dict() if response else {"key": key, "deleted": True}
    return [types.TextContent(type="text", text=str(result))]
