from typing import Callable, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.provider_api import ProviderApi

from src.airflow.airflow_client import api_client

provider_api = ProviderApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_providers, "get_providers", "Get a list of loaded providers", True),
    ]


async def get_providers(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get a list of providers.

    Args:
        limit: The numbers of items to return.
        offset: The number of items to skip before starting to collect the result set.

    Returns:
        A list of providers with their details.
    """
    # GET /providers has no query parameters in the Airflow 2.10 stable REST spec.
    # Keep limit/offset on the tool signature for compatibility; they are not sent.
    _ = (limit, offset)
    response = provider_api.get_providers()
    return [types.TextContent(type="text", text=str(response.to_dict()))]
