from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.pool_api import PoolApi
from airflow_client.client.model.pool import Pool

from src.airflow.airflow_client import api_client

pool_api = PoolApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_pools, "get_pools", "List pools", True),
        (get_pool, "get_pool", "Get a pool by name", True),
        (delete_pool, "delete_pool", "Delete a pool", False),
        (post_pool, "post_pool", "Create a pool", False),
        (patch_pool, "patch_pool", "Update a pool", False),
    ]


async def get_pools(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    List pools.

    Args:
        limit: The numbers of items to return.
        offset: The number of items to skip before starting to collect the result set.
        order_by: The name of the field to order the results by. Prefix a field name with `-` to reverse the sort order.

    Returns:
        A list of pools.
    """
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by

    response = pool_api.get_pools(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_pool(
    pool_name: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get a pool by name.

    Args:
        pool_name: The pool name.

    Returns:
        The pool details.
    """
    response = pool_api.get_pool(pool_name=pool_name)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def delete_pool(
    pool_name: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Delete a pool.

    Args:
        pool_name: The pool name.

    Returns:
        A confirmation message.
    """
    pool_api.delete_pool(pool_name=pool_name)
    return [types.TextContent(type="text", text=f"Pool '{pool_name}' deleted successfully.")]


async def post_pool(
    name: str,
    slots: int,
    description: Optional[str] = None,
    include_deferred: Optional[bool] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Create a pool.

    Args:
        name: The pool name.
        slots: The number of slots.
        description: The pool description.
        include_deferred: Whether to include deferred tasks in slot calculations.

    Returns:
        The created pool details.
    """
    pool = Pool(
        name=name,
        slots=slots,
    )

    if description is not None:
        pool.description = description

    if include_deferred is not None:
        pool.include_deferred = include_deferred

    response = pool_api.post_pool(pool=pool)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def patch_pool(
    pool_name: str,
    slots: Optional[int] = None,
    description: Optional[str] = None,
    include_deferred: Optional[bool] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Update a pool.

    Args:
        pool_name: The pool name.
        slots: The number of slots.
        description: The pool description.
        include_deferred: Whether to include deferred tasks in slot calculations.

    Returns:
        The updated pool details.
    """
    pool = Pool()

    if slots is not None:
        pool.slots = slots

    if description is not None:
        pool.description = description

    if include_deferred is not None:
        pool.include_deferred = include_deferred

    response = pool_api.patch_pool(pool_name=pool_name, pool=pool)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
