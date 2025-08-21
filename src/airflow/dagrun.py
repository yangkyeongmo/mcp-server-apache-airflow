from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.dag_run_api import DAGRunApi
from airflow_client.client.model.clear_dag_run import ClearDagRun
from airflow_client.client.model.dag_run import DAGRun
from airflow_client.client.model.set_dag_run_note import SetDagRunNote
from airflow_client.client.model.update_dag_run_state import UpdateDagRunState

from src.airflow.airflow_client import api_client
from src.envs import AIRFLOW_HOST

dag_run_api = DAGRunApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (post_dag_run, "post_dag_run", "Trigger a DAG by ID", False),
        (get_dag_runs, "get_dag_runs", "Get DAG runs by ID", True),
        (get_dag_runs_batch, "get_dag_runs_batch", "List DAG runs (batch)", True),
        (get_dag_run, "get_dag_run", "Get a DAG run by DAG ID and DAG run ID", True),
        (update_dag_run_state, "update_dag_run_state", "Update a DAG run state by DAG ID and DAG run ID", False),
        (delete_dag_run, "delete_dag_run", "Delete a DAG run by DAG ID and DAG run ID", False),
        (clear_dag_run, "clear_dag_run", "Clear a DAG run", False),
        (set_dag_run_note, "set_dag_run_note", "Update the DagRun note", False),
        (get_upstream_dataset_events, "get_upstream_dataset_events", "Get dataset events for a DAG run", True),
    ]


def get_dag_run_url(dag_id: str, dag_run_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid?dag_run_id={dag_run_id}"


async def post_dag_run(
    dag_id: str,
    dag_run_id: Optional[str] = None,
    data_interval_end: Optional[datetime] = None,
    data_interval_start: Optional[datetime] = None,
    execution_date: Optional[datetime] = None,
    logical_date: Optional[datetime] = None,
    note: Optional[str] = None,
    # state: Optional[str] = None,  # TODO: add state
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build kwargs dictionary with only non-None values
    kwargs = {}

    # Add non-read-only fields that can be set during creation
    if dag_run_id is not None:
        kwargs["dag_run_id"] = dag_run_id
    if data_interval_end is not None:
        kwargs["data_interval_end"] = data_interval_end
    if data_interval_start is not None:
        kwargs["data_interval_start"] = data_interval_start
    if execution_date is not None:
        kwargs["execution_date"] = execution_date
    if logical_date is not None:
        kwargs["logical_date"] = logical_date
    if note is not None:
        kwargs["note"] = note

    # Create DAGRun without read-only fields
    dag_run = DAGRun(**kwargs)

    response = dag_run_api.post_dag_run(dag_id=dag_id, dag_run=dag_run)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_dag_runs(
    dag_id: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    execution_date_gte: Optional[str] = None,
    execution_date_lte: Optional[str] = None,
    start_date_gte: Optional[str] = None,
    start_date_lte: Optional[str] = None,
    end_date_gte: Optional[str] = None,
    end_date_lte: Optional[str] = None,
    updated_at_gte: Optional[str] = None,
    updated_at_lte: Optional[str] = None,
    state: Optional[List[str]] = None,
    order_by: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
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
    if state is not None:
        kwargs["state"] = state
    if order_by is not None:
        kwargs["order_by"] = order_by

    response = dag_run_api.get_dag_runs(dag_id=dag_id, **kwargs)

    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()

    # Add UI links to each DAG run
    for dag_run in response_dict.get("dag_runs", []):
        dag_run["ui_url"] = get_dag_run_url(dag_id, dag_run["dag_run_id"])

    return [types.TextContent(type="text", text=str(response_dict))]


async def get_dag_runs_batch(
    dag_ids: Optional[List[str]] = None,
    execution_date_gte: Optional[str] = None,
    execution_date_lte: Optional[str] = None,
    start_date_gte: Optional[str] = None,
    start_date_lte: Optional[str] = None,
    end_date_gte: Optional[str] = None,
    end_date_lte: Optional[str] = None,
    state: Optional[List[str]] = None,
    order_by: Optional[str] = None,
    page_offset: Optional[int] = None,
    page_limit: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build request dictionary
    request: Dict[str, Any] = {}
    if dag_ids is not None:
        request["dag_ids"] = dag_ids
    if execution_date_gte is not None:
        request["execution_date_gte"] = execution_date_gte
    if execution_date_lte is not None:
        request["execution_date_lte"] = execution_date_lte
    if start_date_gte is not None:
        request["start_date_gte"] = start_date_gte
    if start_date_lte is not None:
        request["start_date_lte"] = start_date_lte
    if end_date_gte is not None:
        request["end_date_gte"] = end_date_gte
    if end_date_lte is not None:
        request["end_date_lte"] = end_date_lte
    if state is not None:
        request["state"] = state
    if order_by is not None:
        request["order_by"] = order_by
    if page_offset is not None:
        request["page_offset"] = page_offset
    if page_limit is not None:
        request["page_limit"] = page_limit

    response = dag_run_api.get_dag_runs_batch(list_dag_runs_form=request)

    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()

    # Add UI links to each DAG run
    for dag_run in response_dict.get("dag_runs", []):
        dag_run["ui_url"] = get_dag_run_url(dag_run["dag_id"], dag_run["dag_run_id"])

    return [types.TextContent(type="text", text=str(response_dict))]


async def get_dag_run(
    dag_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.get_dag_run(dag_id=dag_id, dag_run_id=dag_run_id)

    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()

    # Add UI link to DAG run
    response_dict["ui_url"] = get_dag_run_url(dag_id, dag_run_id)

    return [types.TextContent(type="text", text=str(response_dict))]


async def update_dag_run_state(
    dag_id: str, dag_run_id: str, state: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_dag_run_state = UpdateDagRunState(state=state)
    response = dag_run_api.update_dag_run_state(
        dag_id=dag_id,
        dag_run_id=dag_run_id,
        update_dag_run_state=update_dag_run_state,
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_dag_run(
    dag_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.delete_dag_run(dag_id=dag_id, dag_run_id=dag_run_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def clear_dag_run(
    dag_id: str, dag_run_id: str, dry_run: Optional[bool] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    clear_dag_run = ClearDagRun(dry_run=dry_run)
    response = dag_run_api.clear_dag_run(dag_id=dag_id, dag_run_id=dag_run_id, clear_dag_run=clear_dag_run)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def set_dag_run_note(
    dag_id: str, dag_run_id: str, note: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    set_dag_run_note = SetDagRunNote(note=note)
    response = dag_run_api.set_dag_run_note(dag_id=dag_id, dag_run_id=dag_run_id, set_dag_run_note=set_dag_run_note)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_upstream_dataset_events(
    dag_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.get_upstream_dataset_events(dag_id=dag_id, dag_run_id=dag_run_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
