"""End-to-end MCP tool calls against a real Airflow REST API.

These tests are marked `integration` and are skipped unless AIRFLOW_INTEGRATION=1.
CI starts Airflow 2.10 via docker/airflow/docker-compose.yaml.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def _text(result: list) -> str:
    assert result, "tool returned no content"
    return result[0].text


@pytest.mark.asyncio
async def test_get_health() -> None:
    from src.airflow.monitoring import get_health

    text = _text(await get_health())
    assert "metadatabase" in text


@pytest.mark.asyncio
async def test_get_version() -> None:
    from src.airflow.monitoring import get_version

    text = _text(await get_version())
    assert "version" in text


@pytest.mark.asyncio
async def test_fetch_dags() -> None:
    from src.airflow.dag import get_dags

    text = _text(await get_dags(limit=5))
    assert "dags" in text
    assert "total_entries" in text


@pytest.mark.asyncio
async def test_get_pools_includes_default() -> None:
    from src.airflow.pool import get_pools

    text = _text(await get_pools())
    assert "pools" in text
    assert "default_pool" in text


@pytest.mark.asyncio
async def test_list_variables() -> None:
    from src.airflow.variable import list_variables

    text = _text(await list_variables())
    assert "variables" in text or "total_entries" in text


@pytest.mark.asyncio
async def test_list_connections() -> None:
    from src.airflow.connection import list_connections

    text = _text(await list_connections())
    assert "connections" in text or "total_entries" in text


@pytest.mark.asyncio
async def test_get_import_errors() -> None:
    from src.airflow.importerror import get_import_errors

    text = _text(await get_import_errors())
    assert "import_errors" in text or "total_entries" in text
