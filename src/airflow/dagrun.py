from typing import Any, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.dag_run_api import DAGRunApi

from src.airflow.airflow_client import api_client
from src.envs import AIRFLOW_HOST
from src.server import app

dag_run_api = DAGRunApi(api_client)


def get_dag_run_url(dag_id: str, dag_run_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid?dag_run_id={dag_run_id}"


@app.tool(name="trigger_dag", description="Trigger a DAG by ID")
async def trigger_dag(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.post_dag_run(dag_id=dag_id, dag_run_request={})
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_dag_runs", description="Get DAG runs by ID")
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


@app.tool(name="get_dag_run", description="Get a DAG run by DAG ID and DAG run ID")
async def get_dag_run(
    dag_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.get_dag_run(dag_id=dag_id, dag_run_id=dag_run_id)
    
    # Convert response to dictionary for easier manipulation
    response_dict = response.to_dict()
    
    # Add UI link to DAG run
    response_dict["ui_url"] = get_dag_run_url(dag_id, dag_run_id)
    
    return [types.TextContent(type="text", text=str(response_dict))]


@app.tool(name="update_dag_run", description="Update a DAG run by DAG ID and DAG run ID")
async def update_dag_run(
    dag_id: str, dag_run_id: str, state: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    if state is not None:
        update_request["state"] = state
    
    response = dag_run_api.patch_dag_run(dag_id=dag_id, dag_run_id=dag_run_id, update_mask=list(update_request.keys()), dag_run_request=update_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="delete_dag_run", description="Delete a DAG run by DAG ID and DAG run ID")
async def delete_dag_run(
    dag_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_run_api.delete_dag_run(dag_id=dag_id, dag_run_id=dag_run_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
