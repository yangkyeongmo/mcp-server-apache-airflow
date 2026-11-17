"""DELETE tools accept empty responses and preserve response bodies."""

import ast
from unittest.mock import MagicMock, patch

import mcp.types as types
import pytest

from src.airflow import connection, dag, dagrun, dataset, pool, variable


@pytest.mark.parametrize(
    "module,api_name,tool_name,kwargs,api_kwargs,identifiers",
    [
        (
            connection,
            "connection_api",
            "delete_connection",
            {"conn_id": "test_conn"},
            {"connection_id": "test_conn"},
            {"connection_id": "test_conn"},
        ),
        (dag, "dag_api", "delete_dag", {"dag_id": "test_dag"}, {"dag_id": "test_dag"}, {"dag_id": "test_dag"}),
        (
            dagrun,
            "dag_run_api",
            "delete_dag_run",
            {"dag_id": "test_dag", "dag_run_id": "test_run"},
            {"dag_id": "test_dag", "dag_run_id": "test_run"},
            {"dag_id": "test_dag", "dag_run_id": "test_run"},
        ),
        (
            variable,
            "variable_api",
            "delete_variable",
            {"key": "test_key"},
            {"variable_key": "test_key"},
            {"key": "test_key"},
        ),
        (
            dataset,
            "dataset_api",
            "delete_dag_dataset_queued_event",
            {"dag_id": "test_dag", "uri": "test://dataset"},
            {"dag_id": "test_dag", "uri": "test://dataset"},
            {"dag_id": "test_dag", "uri": "test://dataset"},
        ),
        (
            dataset,
            "dataset_api",
            "delete_dag_dataset_queued_events",
            {"dag_id": "test_dag"},
            {"dag_id": "test_dag"},
            {"dag_id": "test_dag"},
        ),
        (
            dataset,
            "dataset_api",
            "delete_dataset_queued_events",
            {"uri": "test://dataset"},
            {"uri": "test://dataset"},
            {"uri": "test://dataset"},
        ),
        (
            dataset,
            "dataset_api",
            "delete_dag_dataset_queued_events",
            {"dag_id": "test_dag", "before": "2026-01-01T00:00:00Z"},
            {"dag_id": "test_dag", "before": "2026-01-01T00:00:00Z"},
            {"dag_id": "test_dag"},
        ),
        (
            dataset,
            "dataset_api",
            "delete_dataset_queued_events",
            {"uri": "test://dataset", "before": "2026-01-01T00:00:00Z"},
            {"uri": "test://dataset", "before": "2026-01-01T00:00:00Z"},
            {"uri": "test://dataset"},
        ),
    ],
)
@pytest.mark.parametrize("response_kind", ["none", "falsy", "body"])
async def test_delete_response(module, api_name, tool_name, kwargs, api_kwargs, identifiers, response_kind):
    response = None if response_kind == "none" else MagicMock()
    body = {"message": "server response"}
    if response is not None:
        response.__bool__.return_value = response_kind == "body"
        response.to_dict.return_value = body

    with patch.object(module, api_name) as api:
        method = getattr(api, tool_name)
        method.return_value = response
        result = await getattr(module, tool_name)(**kwargs)
        method.assert_called_once_with(**api_kwargs)

    assert len(result) == 1
    assert isinstance(result[0], types.TextContent)
    assert ast.literal_eval(result[0].text) == (body if response_kind == "body" else {**identifiers, "deleted": True})
    if response is not None:
        if response_kind == "body":
            response.to_dict.assert_called_once_with()
        else:
            response.to_dict.assert_not_called()


async def test_delete_pool_empty_response():
    with patch.object(pool, "pool_api") as api:
        api.delete_pool.return_value = None
        result = await pool.delete_pool("test_pool")
        api.delete_pool.assert_called_once_with(pool_name="test_pool")

    assert len(result) == 1
    assert isinstance(result[0], types.TextContent)
    assert result[0].text == "Pool 'test_pool' deleted successfully."
