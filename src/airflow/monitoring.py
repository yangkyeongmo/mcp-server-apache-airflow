from typing import Callable, List, Union

import mcp.types as types
from airflow_client.client.api.monitoring_api import MonitoringApi

from src.airflow.airflow_client import api_client

monitoring_api = MonitoringApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_health, "get_health", "Get instance status", True),
        (get_version, "get_version", "Get version information", True),
    ]


async def get_health() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get the status of Airflow's metadatabase, triggerer and scheduler.
    It includes info about metadatabase and last heartbeat of scheduler and triggerer.
    """
    response = monitoring_api.get_health()
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_version() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get version information about Airflow.
    """
    response = monitoring_api.get_version()
    return [types.TextContent(type="text", text=str(response.to_dict()))]
