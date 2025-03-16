from typing import Any, Dict, List, Optional, Union, Callable

import mcp.types as types
from airflow_client.client.api.provider_api import ProviderApi

from src.airflow.airflow_client import api_client

provider_api = ProviderApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str]]:
    return [
        (get_providers, "get_providers", "List providers"),
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
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    
    response = provider_api.get_providers(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]

