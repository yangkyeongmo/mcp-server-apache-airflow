"""End-to-end MCP tool calls against a live Airflow REST API."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

pytestmark = pytest.mark.integration


def _text(result: list[Any]) -> str:
    assert result, "tool returned no content"
    return result[0].text


@pytest.mark.asyncio
async def test_get_health_against_live_airflow(live_airflow: str) -> None:
    from src.airflow.monitoring import get_health

    text = _text(await get_health())
    lowered = text.lower()
    assert "metadatabase" in lowered or "healthy" in lowered or "status" in lowered


@pytest.mark.asyncio
async def test_get_version_against_live_airflow(live_airflow: str) -> None:
    from src.airflow.monitoring import get_version

    text = _text(await get_version())
    assert "2." in text or "version" in text.lower()


@pytest.mark.asyncio
async def test_fetch_dags_against_live_airflow(live_airflow: str) -> None:
    from src.airflow.dag import get_dags

    text = _text(await get_dags(limit=5))
    assert "dags" in text.lower() or "dag_id" in text.lower()


@pytest.mark.asyncio
async def test_list_pools_against_live_airflow(live_airflow: str) -> None:
    from src.airflow.pool import get_pools

    text = _text(await get_pools())
    assert "default_pool" in text or "pools" in text.lower()


@pytest.mark.asyncio
async def test_variable_round_trip_against_live_airflow(live_airflow: str) -> None:
    from src.airflow.variable import create_variable, delete_variable, get_variable, list_variables

    key = f"mcp_factory_{uuid.uuid4().hex[:12]}"
    value = "integration-value"
    try:
        created = _text(await create_variable(key=key, value=value, description="factory integration"))
        assert key in created or value in created or created

        fetched = _text(await get_variable(key=key))
        assert key in fetched
        assert value in fetched

        listed = _text(await list_variables())
        assert key in listed
    finally:
        await delete_variable(key=key)
