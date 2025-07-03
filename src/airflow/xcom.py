from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.x_com_api import XComApi

from src.airflow.airflow_client import api_client

xcom_api = XComApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_xcom_entries, "get_xcom_entries", "Get all XCom entries", True),
        (get_xcom_entry, "get_xcom_entry", "Get an XCom entry", True),
    ]


async def get_xcom_entries(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
    map_index: Optional[int] = None,
    xcom_key: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if map_index is not None:
        kwargs["map_index"] = map_index
    if xcom_key is not None:
        kwargs["xcom_key"] = xcom_key
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset

    response = xcom_api.get_xcom_entries(dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_xcom_entry(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
    xcom_key: str,
    map_index: Optional[int] = None,
    deserialize: Optional[bool] = None,
    stringify: Optional[bool] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if map_index is not None:
        kwargs["map_index"] = map_index
    if deserialize is not None:
        kwargs["deserialize"] = deserialize
    if stringify is not None:
        kwargs["stringify"] = stringify

    response = xcom_api.get_xcom_entry(
        dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id, xcom_key=xcom_key, **kwargs
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]
