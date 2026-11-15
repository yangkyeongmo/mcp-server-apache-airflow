from typing import Callable, List, Union

import mcp.types as types
from airflow_client.client.api.provider_api import ProviderApi

from src.airflow.airflow_client import api_client

provider_api = ProviderApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_providers, "get_providers", "Get a list of loaded providers", True),
    ]


async def get_providers() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get a list of providers.

    Airflow's stable REST spec for GET /providers has no pagination parameters.

    Returns:
        A list of providers with their details.
    """
    response = provider_api.get_providers()
    return [types.TextContent(type="text", text=str(response.to_dict()))]
