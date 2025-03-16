from typing import Any, Dict, List, Optional, Union, Callable

import mcp.types as types
from airflow_client.client.api.dag_stats_api import DagStatsApi

from src.airflow.airflow_client import api_client

dag_stats_api = DagStatsApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str]]:
    return [
        (get_dag_stats, "get_dag_stats", "Get DAG stats"),
    ]


async def get_dag_stats(
    dag_ids: Optional[List[str]] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if dag_ids is not None:
        kwargs["dag_ids"] = dag_ids
    
    response = dag_stats_api.get_dag_stats(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
