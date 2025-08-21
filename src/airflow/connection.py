from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.connection_api import ConnectionApi

from src.airflow.airflow_client import api_client

connection_api = ConnectionApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (list_connections, "list_connections", "List all connections", True),
        (create_connection, "create_connection", "Create a connection", False),
        (get_connection, "get_connection", "Get a connection by ID", True),
        (update_connection, "update_connection", "Update a connection by ID", False),
        (delete_connection, "delete_connection", "Delete a connection by ID", False),
        (test_connection, "test_connection", "Test a connection", True),
    ]


async def list_connections(
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

    response = connection_api.get_connections(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def create_connection(
    conn_id: str,
    conn_type: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    schema: Optional[str] = None,
    extra: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    connection_request = {
        "connection_id": conn_id,
        "conn_type": conn_type,
    }
    if host is not None:
        connection_request["host"] = host
    if port is not None:
        connection_request["port"] = port
    if login is not None:
        connection_request["login"] = login
    if password is not None:
        connection_request["password"] = password
    if schema is not None:
        connection_request["schema"] = schema
    if extra is not None:
        connection_request["extra"] = extra

    response = connection_api.post_connection(connection_request=connection_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_connection(conn_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = connection_api.get_connection(connection_id=conn_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def update_connection(
    conn_id: str,
    conn_type: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    schema: Optional[str] = None,
    extra: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    if conn_type is not None:
        update_request["conn_type"] = conn_type
    if host is not None:
        update_request["host"] = host
    if port is not None:
        update_request["port"] = port
    if login is not None:
        update_request["login"] = login
    if password is not None:
        update_request["password"] = password
    if schema is not None:
        update_request["schema"] = schema
    if extra is not None:
        update_request["extra"] = extra

    response = connection_api.patch_connection(
        connection_id=conn_id, update_mask=list(update_request.keys()), connection_request=update_request
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_connection(conn_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = connection_api.delete_connection(connection_id=conn_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def test_connection(
    conn_type: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    schema: Optional[str] = None,
    extra: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    connection_request = {
        "conn_type": conn_type,
    }
    if host is not None:
        connection_request["host"] = host
    if port is not None:
        connection_request["port"] = port
    if login is not None:
        connection_request["login"] = login
    if password is not None:
        connection_request["password"] = password
    if schema is not None:
        connection_request["schema"] = schema
    if extra is not None:
        connection_request["extra"] = extra

    response = connection_api.test_connection(connection_request=connection_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
