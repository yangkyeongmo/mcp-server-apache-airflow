from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.dag_api import DAGApi
from airflow_client.client.model.clear_task_instances import ClearTaskInstances
from airflow_client.client.model.dag import DAG
from airflow_client.client.model.update_task_instances_state import UpdateTaskInstancesState

from src.airflow.airflow_client import api_client
from src.envs import AIRFLOW_HOST

dag_api = DAGApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_dags, "fetch_dags", "Fetch all DAGs", True),
        (get_dag, "get_dag", "Get a DAG by ID", True),
        (get_dag_details, "get_dag_details", "Get a simplified representation of DAG", True),
        (get_dag_source, "get_dag_source", "Get a source code", True),
        (pause_dag, "pause_dag", "Pause a DAG by ID", False),
        (unpause_dag, "unpause_dag", "Unpause a DAG by ID", False),
        (get_dag_tasks, "get_dag_tasks", "Get tasks for DAG", True),
        (get_task, "get_task", "Get a task by ID", True),
        (get_tasks, "get_tasks", "Get tasks for DAG", True),
        (patch_dag, "patch_dag", "Update a DAG", False),
        (patch_dags, "patch_dags", "Update multiple DAGs", False),
        (delete_dag, "delete_dag", "Delete a DAG", False),
        (clear_task_instances, "clear_task_instances", "Clear a set of task instances", False),
        (set_task_instances_state, "set_task_instances_state", "Set a state of task instances", False),
        (reparse_dag_file, "reparse_dag_file", "Request re-parsing of a DAG file", False),
    ]


def get_dag_url(dag_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid"


async def get_dags(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    tags: Optional[List[str]] = None,
    only_active: Optional[bool] = None,
    paused: Optional[bool] = None,
    dag_id_pattern: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by
    if tags is not None:
        kwargs["tags"] = tags
    if only_active is not None:
        kwargs["only_active"] = only_active
    if paused is not None:
        kwargs["paused"] = paused
    if dag_id_pattern is not None:
        kwargs["dag_id_pattern"] = dag_id_pattern

    # Use the client to fetch DAGs
    response = dag_api.get_dags(**kwargs)

    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()

    # Add UI links to each DAG
    for dag in response_dict.get("dags", []):
        dag["ui_url"] = get_dag_url(dag["dag_id"])

    return [types.TextContent(type="text", text=str(response_dict))]


async def get_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_dag(dag_id=dag_id)

    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()

    # Add UI link to DAG
    response_dict["ui_url"] = get_dag_url(dag_id)

    return [types.TextContent(type="text", text=str(response_dict))]


async def get_dag_details(
    dag_id: str, fields: Optional[List[str]] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if fields is not None:
        kwargs["fields"] = fields

    response = dag_api.get_dag_details(dag_id=dag_id, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dag_source(file_token: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_dag_source(file_token=file_token)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def pause_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    dag = DAG(is_paused=True)
    response = dag_api.patch_dag(dag_id=dag_id, dag=dag, update_mask=["is_paused"])
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def unpause_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    dag = DAG(is_paused=False)
    response = dag_api.patch_dag(dag_id=dag_id, dag=dag, update_mask=["is_paused"])
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dag_tasks(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_tasks(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def patch_dag(
    dag_id: str, is_paused: Optional[bool] = None, tags: Optional[List[str]] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    update_mask = []

    if is_paused is not None:
        update_request["is_paused"] = is_paused
        update_mask.append("is_paused")
    if tags is not None:
        update_request["tags"] = tags
        update_mask.append("tags")

    dag = DAG(**update_request)

    response = dag_api.patch_dag(dag_id=dag_id, dag=dag, update_mask=update_mask)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def patch_dags(
    dag_id_pattern: Optional[str] = None,
    is_paused: Optional[bool] = None,
    tags: Optional[List[str]] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    update_mask = []

    if is_paused is not None:
        update_request["is_paused"] = is_paused
        update_mask.append("is_paused")
    if tags is not None:
        update_request["tags"] = tags
        update_mask.append("tags")

    dag = DAG(**update_request)

    kwargs = {}
    if dag_id_pattern is not None:
        kwargs["dag_id_pattern"] = dag_id_pattern

    response = dag_api.patch_dags(dag_id_pattern=dag_id_pattern, dag=dag, update_mask=update_mask, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.delete_dag(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_task(
    dag_id: str, task_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_task(dag_id=dag_id, task_id=task_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_tasks(
    dag_id: str, order_by: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    kwargs = {}
    if order_by is not None:
        kwargs["order_by"] = order_by

    response = dag_api.get_tasks(dag_id=dag_id, **kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def clear_task_instances(
    dag_id: str,
    task_ids: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_subdags: Optional[bool] = None,
    include_parentdag: Optional[bool] = None,
    include_upstream: Optional[bool] = None,
    include_downstream: Optional[bool] = None,
    include_future: Optional[bool] = None,
    include_past: Optional[bool] = None,
    dry_run: Optional[bool] = None,
    reset_dag_runs: Optional[bool] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    clear_request = {}
    if task_ids is not None:
        clear_request["task_ids"] = task_ids
    if start_date is not None:
        clear_request["start_date"] = start_date
    if end_date is not None:
        clear_request["end_date"] = end_date
    if include_subdags is not None:
        clear_request["include_subdags"] = include_subdags
    if include_parentdag is not None:
        clear_request["include_parentdag"] = include_parentdag
    if include_upstream is not None:
        clear_request["include_upstream"] = include_upstream
    if include_downstream is not None:
        clear_request["include_downstream"] = include_downstream
    if include_future is not None:
        clear_request["include_future"] = include_future
    if include_past is not None:
        clear_request["include_past"] = include_past
    if dry_run is not None:
        clear_request["dry_run"] = dry_run
    if reset_dag_runs is not None:
        clear_request["reset_dag_runs"] = reset_dag_runs

    clear_task_instances = ClearTaskInstances(**clear_request)

    response = dag_api.post_clear_task_instances(dag_id=dag_id, clear_task_instances=clear_task_instances)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def set_task_instances_state(
    dag_id: str,
    state: str,
    task_ids: Optional[List[str]] = None,
    execution_date: Optional[str] = None,
    include_upstream: Optional[bool] = None,
    include_downstream: Optional[bool] = None,
    include_future: Optional[bool] = None,
    include_past: Optional[bool] = None,
    dry_run: Optional[bool] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    state_request = {"state": state}
    if task_ids is not None:
        state_request["task_ids"] = task_ids
    if execution_date is not None:
        state_request["execution_date"] = execution_date
    if include_upstream is not None:
        state_request["include_upstream"] = include_upstream
    if include_downstream is not None:
        state_request["include_downstream"] = include_downstream
    if include_future is not None:
        state_request["include_future"] = include_future
    if include_past is not None:
        state_request["include_past"] = include_past
    if dry_run is not None:
        state_request["dry_run"] = dry_run

    update_task_instances_state = UpdateTaskInstancesState(**state_request)

    response = dag_api.post_set_task_instances_state(
        dag_id=dag_id,
        update_task_instances_state=update_task_instances_state,
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def reparse_dag_file(
    file_token: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.reparse_dag_file(file_token=file_token)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
