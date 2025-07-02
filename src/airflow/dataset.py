from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.dataset_api import DatasetApi

from src.airflow.airflow_client import api_client

dataset_api = DatasetApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_datasets, "get_datasets", "List datasets", True),
        (get_dataset, "get_dataset", "Get a dataset by URI", True),
        (get_dataset_events, "get_dataset_events", "Get dataset events", True),
        (create_dataset_event, "create_dataset_event", "Create dataset event", False),
        (get_dag_dataset_queued_event, "get_dag_dataset_queued_event", "Get a queued Dataset event for a DAG", True),
        (get_dag_dataset_queued_events, "get_dag_dataset_queued_events", "Get queued Dataset events for a DAG", True),
        (
            delete_dag_dataset_queued_event,
            "delete_dag_dataset_queued_event",
            "Delete a queued Dataset event for a DAG",
            False,
        ),
        (
            delete_dag_dataset_queued_events,
            "delete_dag_dataset_queued_events",
            "Delete queued Dataset events for a DAG",
            False,
        ),
        (get_dataset_queued_events, "get_dataset_queued_events", "Get queued Dataset events for a Dataset", True),
        (
            delete_dataset_queued_events,
            "delete_dataset_queued_events",
            "Delete queued Dataset events for a Dataset",
            False,
        ),
    ]


async def get_datasets(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    uri_pattern: Optional[str] = None,
    dag_ids: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by
    if uri_pattern is not None:
        kwargs["uri_pattern"] = uri_pattern
    if dag_ids is not None:
        kwargs["dag_ids"] = dag_ids

    response = dataset_api.get_datasets(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dataset(
    uri: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dataset_api.get_dataset(uri=uri)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dataset_events(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    dataset_id: Optional[int] = None,
    source_dag_id: Optional[str] = None,
    source_task_id: Optional[str] = None,
    source_run_id: Optional[str] = None,
    source_map_index: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by
    if dataset_id is not None:
        kwargs["dataset_id"] = dataset_id
    if source_dag_id is not None:
        kwargs["source_dag_id"] = source_dag_id
    if source_task_id is not None:
        kwargs["source_task_id"] = source_task_id
    if source_run_id is not None:
        kwargs["source_run_id"] = source_run_id
    if source_map_index is not None:
        kwargs["source_map_index"] = source_map_index

    response = dataset_api.get_dataset_events(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def create_dataset_event(
    dataset_uri: str,
    extra: Optional[Dict[str, Any]] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    event_request = {
        "dataset_uri": dataset_uri,
    }
    if extra is not None:
        event_request["extra"] = extra

    response = dataset_api.create_dataset_event(create_dataset_event=event_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dag_dataset_queued_event(
    dag_id: str,
    uri: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dataset_api.get_dag_dataset_queued_event(dag_id=dag_id, uri=uri)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dag_dataset_queued_events(
    dag_id: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dataset_api.get_dag_dataset_queued_events(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_dag_dataset_queued_event(
    dag_id: str,
    uri: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dataset_api.delete_dag_dataset_queued_event(dag_id=dag_id, uri=uri)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_dag_dataset_queued_events(
    dag_id: str,
    before: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    kwargs: Dict[str, Any] = {}
    if before is not None:
        kwargs["before"] = before

    response = dataset_api.delete_dag_dataset_queued_events(dag_id=dag_id, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dataset_queued_events(
    uri: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dataset_api.get_dataset_queued_events(uri=uri)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_dataset_queued_events(
    uri: str,
    before: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    kwargs: Dict[str, Any] = {}
    if before is not None:
        kwargs["before"] = before

    response = dataset_api.delete_dataset_queued_events(uri=uri, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
