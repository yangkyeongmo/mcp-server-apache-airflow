from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.task_instance_api import TaskInstanceApi

from src.airflow.airflow_client import api_client

task_instance_api = TaskInstanceApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_task_instance, "get_task_instance", "Get a task instance by DAG ID, task ID, and DAG run ID", True),
        (list_task_instances, "list_task_instances", "List task instances by DAG ID and DAG run ID", True),
        (
            update_task_instance,
            "update_task_instance",
            "Update a task instance by DAG ID, DAG run ID, and task ID",
            False,
        ),
        (
            get_log,
            "get_log",
            "Get the log from a task instance by DAG ID, task ID, DAG run ID and task try number",
            True,
        ),
        (
            list_task_instance_tries,
            "list_task_instance_tries",
            "List task instance tries by DAG ID, DAG run ID, and task ID",
            True,
        ),
    ]


async def get_task_instance(
    dag_id: str, task_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = task_instance_api.get_task_instance(dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def list_task_instances(
    dag_id: str,
    dag_run_id: str,
    execution_date_gte: Optional[str] = None,
    execution_date_lte: Optional[str] = None,
    start_date_gte: Optional[str] = None,
    start_date_lte: Optional[str] = None,
    end_date_gte: Optional[str] = None,
    end_date_lte: Optional[str] = None,
    updated_at_gte: Optional[str] = None,
    updated_at_lte: Optional[str] = None,
    duration_gte: Optional[float] = None,
    duration_lte: Optional[float] = None,
    state: Optional[List[str]] = None,
    pool: Optional[List[str]] = None,
    queue: Optional[List[str]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if execution_date_gte is not None:
        kwargs["execution_date_gte"] = execution_date_gte
    if execution_date_lte is not None:
        kwargs["execution_date_lte"] = execution_date_lte
    if start_date_gte is not None:
        kwargs["start_date_gte"] = start_date_gte
    if start_date_lte is not None:
        kwargs["start_date_lte"] = start_date_lte
    if end_date_gte is not None:
        kwargs["end_date_gte"] = end_date_gte
    if end_date_lte is not None:
        kwargs["end_date_lte"] = end_date_lte
    if updated_at_gte is not None:
        kwargs["updated_at_gte"] = updated_at_gte
    if updated_at_lte is not None:
        kwargs["updated_at_lte"] = updated_at_lte
    if duration_gte is not None:
        kwargs["duration_gte"] = duration_gte
    if duration_lte is not None:
        kwargs["duration_lte"] = duration_lte
    if state is not None:
        kwargs["state"] = state
    if pool is not None:
        kwargs["pool"] = pool
    if queue is not None:
        kwargs["queue"] = queue
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset

    response = task_instance_api.get_task_instances(dag_id=dag_id, dag_run_id=dag_run_id, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def update_task_instance(
    dag_id: str, dag_run_id: str, task_id: str, state: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    if state is not None:
        update_request["state"] = state

    response = task_instance_api.patch_task_instance(
        dag_id=dag_id,
        dag_run_id=dag_run_id,
        task_id=task_id,
        update_mask=list(update_request.keys()),
        task_instance_request=update_request,
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_log(
    dag_id: str, task_id: str, dag_run_id: str, task_try_number: int
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = task_instance_api.get_log(
        dag_id=dag_id,
        dag_run_id=dag_run_id,
        task_id=task_id,
        task_try_number=task_try_number,
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def list_task_instance_tries(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
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

    response = task_instance_api.get_task_instance_tries(
        dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id, **kwargs
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]
