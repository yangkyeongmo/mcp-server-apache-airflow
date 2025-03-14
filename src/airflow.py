from typing import Any, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client import ApiClient, Configuration
from airflow_client.client.api.dag_api import DAGApi
from airflow_client.client.api.dag_run_api import DAGRunApi
from airflow_client.client.api.import_error_api import ImportErrorApi
from airflow_client.client.api.monitoring_api import MonitoringApi
from airflow_client.client.api.task_instance_api import TaskInstanceApi

from src.envs import AIRFLOW_HOST, AIRFLOW_PASSWORD, AIRFLOW_USERNAME

# Create a configuration and API client
configuration = Configuration(
    host=AIRFLOW_HOST,
    username=AIRFLOW_USERNAME,
    password=AIRFLOW_PASSWORD,
)
api_client = ApiClient(configuration)

# Create API instances
dag_api = DAGApi(api_client)
dag_run_api = DAGRunApi(api_client)
task_instance_api = TaskInstanceApi(api_client)
import_error_api = ImportErrorApi(api_client)
monitoring_api = MonitoringApi(api_client)


def get_dag_url(dag_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid"


def get_dag_run_url(dag_id: str, dag_run_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid?dag_run_id={dag_run_id}"


def get_task_instance_url(dag_id: str, dag_run_id: str, task_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid?dag_run_id={dag_run_id}&task_id={task_id}"


async def fetch_dags(
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


async def pause_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.patch_dag(dag_id=dag_id, dag_update_request={"is_paused": True})
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def unpause_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.patch_dag(dag_id=dag_id, dag_update_request={"is_paused": False})
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def trigger_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.post_dag_run(dag_id=dag_id, dag_run_request={})
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


async def get_dag_tasks(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_tasks(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


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


async def get_import_error(
    import_error_id: int,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = import_error_api.get_import_error(import_error_id=import_error_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def list_import_errors(
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

    response = import_error_api.get_import_errors(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_health() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = monitoring_api.get_health()
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_version() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = monitoring_api.get_version()
    return [types.TextContent(type="text", text=str(response.to_dict()))]
