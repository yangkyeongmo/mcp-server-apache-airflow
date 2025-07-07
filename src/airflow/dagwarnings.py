from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.dag_warning_api import DagWarningApi

from src.airflow.airflow_client import api_client

dag_warnings_api = DagWarningApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_dag_warnings, "get_dag_warnings", "Get DAG warnings", True),
    ]


async def get_dag_warnings(
    dag_id: Optional[str] = None,
    warning_type: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if dag_id is not None:
        kwargs["dag_id"] = dag_id
    if warning_type is not None:
        kwargs["warning_type"] = warning_type
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by

    response = dag_warnings_api.get_dag_warnings(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
