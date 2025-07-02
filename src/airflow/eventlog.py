from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.event_log_api import EventLogApi

from src.airflow.airflow_client import api_client

event_log_api = EventLogApi(api_client)


def get_all_functions() -> list[tuple[Callable, str, str, bool]]:
    """Return list of (function, name, description, is_read_only) tuples for registration."""
    return [
        (get_event_logs, "get_event_logs", "List log entries from event log", True),
        (get_event_log, "get_event_log", "Get a specific log entry by ID", True),
    ]


async def get_event_logs(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    dag_id: Optional[str] = None,
    task_id: Optional[str] = None,
    run_id: Optional[str] = None,
    map_index: Optional[int] = None,
    try_number: Optional[int] = None,
    event: Optional[str] = None,
    owner: Optional[str] = None,
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    included_events: Optional[str] = None,
    excluded_events: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by
    if dag_id is not None:
        kwargs["dag_id"] = dag_id
    if task_id is not None:
        kwargs["task_id"] = task_id
    if run_id is not None:
        kwargs["run_id"] = run_id
    if map_index is not None:
        kwargs["map_index"] = map_index
    if try_number is not None:
        kwargs["try_number"] = try_number
    if event is not None:
        kwargs["event"] = event
    if owner is not None:
        kwargs["owner"] = owner
    if before is not None:
        kwargs["before"] = before
    if after is not None:
        kwargs["after"] = after
    if included_events is not None:
        kwargs["included_events"] = included_events
    if excluded_events is not None:
        kwargs["excluded_events"] = excluded_events

    response = event_log_api.get_event_logs(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


async def get_event_log(
    event_log_id: int,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = event_log_api.get_event_log(event_log_id=event_log_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
