from typing import Callable
import mcp.types as types
from airflow_client.client.api.monitoring_api import MonitoringApi

from src.airflow.airflow_client import api_client

monitoring_api = MonitoringApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str]]:
    return [
        (get_health, "get_health", "Get health"),
        (get_version, "get_version", "Get version"),
    ]


async def get_health() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    response = monitoring_api.get_health()
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_version() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    response = monitoring_api.get_version()
    return [types.TextContent(type="text", text=str(response.to_dict()))]