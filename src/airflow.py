import os

import httpx
import mcp.types as types

AIRFLOW_HOST = os.getenv("AIRFLOW_HOST").rstrip("/")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

def get_dag_url(dag_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid"

def get_dag_run_url(dag_id: str, dag_run_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid?dag_run_id={dag_run_id}"

def get_task_instance_url(dag_id: str, dag_run_id: str, task_id: str) -> str:
    return f"{AIRFLOW_HOST}/dags/{dag_id}/grid?dag_run_id={dag_run_id}&task_id={task_id}"

async def fetch_dags(
    limit: int | None = None,
    offset: int | None = None,
    order_by: str | None = None,
    tags: list[str] | None = None,
    only_active: bool | None = None,
    paused: bool | None = None,
    dag_id_pattern: str | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = "/api/v1/dags"
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if order_by is not None:
        params["order_by"] = order_by
    if tags is not None:
        params["tags"] = tags
    if only_active is not None:
        params["only_active"] = only_active
    if paused is not None:
        params["paused"] = paused
    if dag_id_pattern is not None:
        params["dag_id_pattern"] = dag_id_pattern

    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        # Add UI links to each DAG
        for dag in data.get("dags", []):
            dag["ui_url"] = get_dag_url(dag["dag_id"])
            
        return [types.TextContent(type="text", text=response.text)]

async def get_dag(dag_id: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        response.raise_for_status()
        data = response.json()
        
        # Add UI link to DAG
        data["ui_url"] = get_dag_url(dag_id)
        
        return [types.TextContent(type="text", text=response.text)]

async def pause_dag(dag_id: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.patch(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            json={"is_paused": True}
        )
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def unpause_dag(dag_id: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.patch(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            json={"is_paused": False}
        )
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def trigger_dag(dag_id: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}/dagRuns"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.post(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            json={}
        )
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def get_dag_runs(
    dag_id: str,
    limit: int | None = None,
    offset: int | None = None,
    execution_date_gte: str | None = None,
    execution_date_lte: str | None = None,
    start_date_gte: str | None = None,
    start_date_lte: str | None = None,
    end_date_gte: str | None = None,
    end_date_lte: str | None = None,
    updated_at_gte: str | None = None,
    updated_at_lte: str | None = None,
    state: list[str] | None = None,
    order_by: str | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}/dagRuns"
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if execution_date_gte is not None:
        params["execution_date_gte"] = execution_date_gte
    if execution_date_lte is not None:
        params["execution_date_lte"] = execution_date_lte
    if start_date_gte is not None:
        params["start_date_gte"] = start_date_gte
    if start_date_lte is not None:
        params["start_date_lte"] = start_date_lte
    if end_date_gte is not None:
        params["end_date_gte"] = end_date_gte
    if end_date_lte is not None:
        params["end_date_lte"] = end_date_lte
    if updated_at_gte is not None:
        params["updated_at_gte"] = updated_at_gte
    if updated_at_lte is not None:
        params["updated_at_lte"] = updated_at_lte
    if state is not None:
        params["state"] = state
    if order_by is not None:
        params["order_by"] = order_by

    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        # Add UI links to each DAG run
        for dag_run in data.get("dag_runs", []):
            dag_run["ui_url"] = get_dag_run_url(dag_id, dag_run["dag_run_id"])
            
        return [types.TextContent(type="text", text=response.text)]

async def get_dag_tasks(dag_id: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}/tasks"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def get_task_instance(dag_id: str, task_id: str, dag_run_id: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def list_task_instances(
    dag_id: str,
    dag_run_id: str,
    execution_date_gte: str | None = None,
    execution_date_lte: str | None = None,
    start_date_gte: str | None = None,
    start_date_lte: str | None = None,
    end_date_gte: str | None = None,
    end_date_lte: str | None = None,
    updated_at_gte: str | None = None,
    updated_at_lte: str | None = None,
    duration_gte: float | None = None,
    duration_lte: float | None = None,
    state: list[str] | None = None,
    pool: list[str] | None = None,
    queue: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances"
    params = {}
    if execution_date_gte is not None:
        params["execution_date_gte"] = execution_date_gte
    if execution_date_lte is not None:
        params["execution_date_lte"] = execution_date_lte
    if start_date_gte is not None:
        params["start_date_gte"] = start_date_gte
    if start_date_lte is not None:
        params["start_date_lte"] = start_date_lte
    if end_date_gte is not None:
        params["end_date_gte"] = end_date_gte
    if end_date_lte is not None:
        params["end_date_lte"] = end_date_lte
    if updated_at_gte is not None:
        params["updated_at_gte"] = updated_at_gte
    if updated_at_lte is not None:
        params["updated_at_lte"] = updated_at_lte
    if duration_gte is not None:
        params["duration_gte"] = duration_gte
    if duration_lte is not None:
        params["duration_lte"] = duration_lte
    if state is not None:
        params["state"] = state
    if pool is not None:
        params["pool"] = pool
    if queue is not None:
        params["queue"] = queue
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            params=params
        )
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def get_import_error(import_error_id: int) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = f"/api/v1/importErrors/{import_error_id}"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def list_import_errors(
    limit: int | None = None,
    offset: int | None = None,
    order_by: str | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = "/api/v1/importErrors"
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if order_by is not None:
        params["order_by"] = order_by

    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            url, 
            auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            params=params
        )
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def get_health() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = "/api/v1/health"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def get_version() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    path = "/api/v1/version"
    url = f"{AIRFLOW_HOST}{path}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, auth=httpx.BasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)] 
