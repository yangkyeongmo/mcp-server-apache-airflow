from typing import Any, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.dag_api import DAGApi

from src.airflow.airflow_client import api_client
from src.envs import AIRFLOW_HOST
from src.server import app

dag_api = DAGApi(api_client)


def get_dag_url(dag_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid"


@app.tool(name="fetch_dags", description="Fetch all DAGs")
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


@app.tool(name="get_dag", description="Get a DAG by ID")
async def get_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_dag(dag_id=dag_id)

    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()

    # Add UI link to DAG
    response_dict["ui_url"] = get_dag_url(dag_id)

    return [types.TextContent(type="text", text=str(response_dict))]


@app.tool(name="pause_dag", description="Pause a DAG by ID")
async def pause_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.patch_dag(dag_id=dag_id, dag_update_request={"is_paused": True})
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="unpause_dag", description="Unpause a DAG by ID")
async def unpause_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.patch_dag(dag_id=dag_id, dag_update_request={"is_paused": False})
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_dag_tasks", description="Get tasks by DAG ID")
async def get_dag_tasks(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_tasks(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]

@app.tool(name="update_dag", description="Update a DAG by ID")
async def update_dag(
    dag_id: str, is_paused: Optional[bool] = None, tags: Optional[List[str]] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    if is_paused is not None:
        update_request["is_paused"] = is_paused
    if tags is not None:
        update_request["tags"] = tags
    
    response = dag_api.patch_dag(dag_id=dag_id, dag_update_request=update_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="delete_dag", description="Delete a DAG by ID")
async def delete_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.delete_dag(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_task", description="Get a task by DAG ID and task ID")
async def get_task(
    dag_id: str, task_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_task(dag_id=dag_id, task_id=task_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
