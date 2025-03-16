import mcp.types as types
from airflow_client.client.api.monitoring_api import MonitoringApi

from src.airflow.airflow_client import api_client
from src.server import app

monitoring_api = MonitoringApi(api_client)


@app.tool(name="get_health", description="Get health")
async def get_health() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    response = monitoring_api.get_health()
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="get_version", description="Get version")
async def get_version() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    response = monitoring_api.get_version()
    return [types.TextContent(type="text", text=str(response.to_dict()))]