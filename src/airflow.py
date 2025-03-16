from typing import Any, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client import ApiClient, Configuration
from airflow_client.client.api.dag_api import DAGApi
from airflow_client.client.api.dag_run_api import DAGRunApi
from airflow_client.client.api.import_error_api import ImportErrorApi
from airflow_client.client.api.monitoring_api import MonitoringApi
from airflow_client.client.api.task_instance_api import TaskInstanceApi

from src.envs import AIRFLOW_HOST, AIRFLOW_PASSWORD, AIRFLOW_USERNAME
from src.server import app

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


@app.tool(name="get_dag_tasks", description="Get tasks by DAG ID")
async def get_dag_tasks(dag_id: str) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_tasks(dag_id=dag_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_task_instance", description="Get a task instance by DAG ID, task ID, and DAG run ID")
async def get_task_instance(
    dag_id: str, task_id: str, dag_run_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = task_instance_api.get_task_instance(dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="list_task_instances", description="List task instances by DAG ID and DAG run ID")
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


@app.tool(name="get_import_error", description="Get an import error by ID")
async def get_import_error(
    import_error_id: int,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = import_error_api.get_import_error(import_error_id=import_error_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="list_import_errors", description="List import errors")
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


@app.tool(name="get_health", description="Get health")
async def get_health() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = monitoring_api.get_health()
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_version", description="Get version")
async def get_version() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = monitoring_api.get_version()
    return [types.TextContent(type="text", text=str(response.to_dict()))]


# DAG Management
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


# DAG Runs
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


# Tasks
@app.tool(name="get_task", description="Get a task by DAG ID and task ID")
async def get_task(
    dag_id: str, task_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = dag_api.get_task(dag_id=dag_id, task_id=task_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="update_task_instance", description="Update a task instance by DAG ID, DAG run ID, and task ID")
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
        task_instance_request=update_request
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


# Variables
from airflow_client.client.api.variable_api import VariableApi
variable_api = VariableApi(api_client)

@app.tool(name="list_variables", description="List all variables")
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


@app.tool(name="create_variable", description="Create a variable")
async def create_variable(
    key: str, value: str, description: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    variable_request = {
        "key": key,
        "value": value,
    }
    if description is not None:
        variable_request["description"] = description
    
    response = variable_api.post_variables(variable_request=variable_request)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_variable", description="Get a variable by key")
async def get_variable(
    key: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = variable_api.get_variable(variable_key=key)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="update_variable", description="Update a variable by key")
async def update_variable(
    key: str, value: Optional[str] = None, description: Optional[str] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    update_request = {}
    if value is not None:
        update_request["value"] = value
    if description is not None:
        update_request["description"] = description
    
    response = variable_api.patch_variable(
        variable_key=key,
        update_mask=list(update_request.keys()),
        variable_request=update_request
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="delete_variable", description="Delete a variable by key")
async def delete_variable(
    key: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = variable_api.delete_variable(variable_key=key)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


# Connections
from airflow_client.client.api.connection_api import ConnectionApi
connection_api = ConnectionApi(api_client)

@app.tool(name="list_connections", description="List all connections")
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


@app.tool(name="create_connection", description="Create a connection")
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


@app.tool(name="get_connection", description="Get a connection by ID")
async def get_connection(
    conn_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = connection_api.get_connection(connection_id=conn_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="update_connection", description="Update a connection by ID")
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
        connection_id=conn_id,
        update_mask=list(update_request.keys()),
        connection_request=update_request
    )
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="delete_connection", description="Delete a connection by ID")
async def delete_connection(
    conn_id: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = connection_api.delete_connection(connection_id=conn_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
