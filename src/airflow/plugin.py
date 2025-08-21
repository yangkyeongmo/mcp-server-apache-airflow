from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.plugin_api import PluginApi

from src.airflow.airflow_client import api_client

plugin_api = PluginApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_plugins, "get_plugins", "Get a list of loaded plugins", True),
    ]


async def get_plugins(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get a list of loaded plugins.

    Args:
        limit: The numbers of items to return.
        offset: The number of items to skip before starting to collect the result set.

    Returns:
        A list of loaded plugins.
    """
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset

    response = plugin_api.get_plugins(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
