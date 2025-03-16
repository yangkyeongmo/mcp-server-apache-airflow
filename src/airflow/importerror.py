from typing import Any, Dict, List, Optional, Union

import mcp.types as types
from airflow_client.client.api.import_error_api import ImportErrorApi

from src.airflow.airflow_client import api_client
from src.server import app


import_error_api = ImportErrorApi(api_client)


@app.tool(name="get_import_error", description="Get an import error by ID")
async def get_import_error(
    import_error_id: int,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    response = import_error_api.get_import_error(import_error_id=import_error_id)
    return [types.TextContent(type="text", text=str(response.to_dict()))]


@app.tool(name="list_import_errors", description="List import errors")
async def list_import_errors(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    # Build parameters dictionary
    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if offset is not None:
        kwargs["offset"] = offset
    if order_by is not None:
        kwargs["order_by"] = order_by

    response = import_error_api.get_import_errors(**kwargs)
    return [types.TextContent(type="text", text=str(response.to_dict()))]
