from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.config_api import ConfigApi

from src.airflow.airflow_client import api_client

config_api = ConfigApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str]]:
    return [
        (get_config, "get_config", "Get current configuration"),
        (get_value, "get_value", "Get a specific option from configuration"),
    ]


async def get_config(
    section: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if section is not None:
        kwargs["section"] = section

    response = config_api.get_config(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_value(
    section: str, option: str
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = config_api.get_value(section=section, option=option)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
