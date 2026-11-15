"""MCP-protocol E2E against a live Airflow REST API via stdio."""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx
import pytest
from mcp import ClientSession

from test.mcp.stdio import mcp_stdio_session, parse_tool_payload

pytestmark = pytest.mark.e2e_mcp


@pytest.fixture(scope="session")
def live_airflow() -> Iterator[str]:
    if os.environ.get("AIRFLOW_MAJOR") == "3":
        pytest.skip("Airflow 3.x MCP e2e is blocked by apache-airflow-client>=2.7.0,<3")

    os.environ.setdefault("AIRFLOW_HOST", "http://127.0.0.1:8080")
    os.environ.setdefault("AIRFLOW_USERNAME", "airflow")
    os.environ.setdefault("AIRFLOW_PASSWORD", "airflow")
    os.environ.setdefault("AIRFLOW_API_VERSION", "v1")
    base = os.environ["AIRFLOW_HOST"].rstrip("/")
    health_url = f"{base}/api/v1/health"
    try:
        response = httpx.get(
            health_url,
            auth=(os.environ["AIRFLOW_USERNAME"], os.environ["AIRFLOW_PASSWORD"]),
            timeout=5.0,
        )
        if response.status_code in {401, 403}:
            response = httpx.get(health_url, timeout=5.0)
        response.raise_for_status()
    except Exception as exc:
        if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("AIRFLOW_INTEGRATION_REQUIRED") == "1":
            raise RuntimeError(f"Airflow health check failed at {health_url}: {exc}") from exc
        pytest.skip(f"Live Airflow is not available at {health_url}: {exc}")
    yield base


@pytest.fixture
async def mcp_session(live_airflow: str) -> AsyncIterator[ClientSession]:
    async with mcp_stdio_session() as session:
        yield session


async def _call(session: ClientSession, name: str, arguments: dict[str, Any] | None = None) -> Any:
    result = await session.call_tool(name, arguments or {})
    payload = parse_tool_payload(result)
    assert payload not in (None, "", []), f"{name} returned empty payload: {result}"
    return payload


def _as_dict(payload: Any) -> dict[str, Any]:
    assert isinstance(payload, dict), f"expected object payload, got {type(payload)}: {payload!r}"
    return payload


@pytest.mark.asyncio
async def test_protocol_lists_tools(mcp_session: ClientSession) -> None:
    listed = await mcp_session.list_tools()
    names = {tool.name for tool in listed.tools}
    expected = {
        "fetch_dags",
        "get_dag",
        "post_dag_run",
        "get_dag_run",
        "create_variable",
        "get_variable",
        "delete_variable",
        "create_connection",
        "get_connection",
        "delete_connection",
        "get_pools",
        "get_health",
        "get_version",
    }
    missing = expected - names
    assert not missing, f"stdio tools/list missing {sorted(missing)}"


@pytest.mark.asyncio
async def test_protocol_health_and_version(mcp_session: ClientSession) -> None:
    health = _as_dict(await _call(mcp_session, "get_health"))
    assert "metadatabase" in health or "status" in str(health).lower()

    version = _as_dict(await _call(mcp_session, "get_version"))
    assert "version" in version
    assert str(version["version"]).startswith("2.")


@pytest.mark.asyncio
async def test_protocol_list_and_get_dag(mcp_session: ClientSession) -> None:
    listed = _as_dict(await _call(mcp_session, "fetch_dags", {"limit": 10}))
    dags = listed.get("dags")
    assert isinstance(dags, list) and dags, f"fetch_dags returned no dags: {listed}"
    dag_id = dags[0]["dag_id"]
    assert isinstance(dag_id, str) and dag_id

    dag = _as_dict(await _call(mcp_session, "get_dag", {"dag_id": dag_id}))
    assert dag.get("dag_id") == dag_id


@pytest.mark.asyncio
async def test_protocol_trigger_dag_run_and_read_status(mcp_session: ClientSession) -> None:
    listed = _as_dict(await _call(mcp_session, "fetch_dags", {"limit": 20}))
    dags = listed.get("dags") or []
    dag_id = next((item["dag_id"] for item in dags if item.get("dag_id") == "example_bash_operator"), None)
    if dag_id is None:
        assert dags, "fetch_dags returned no dags to trigger"
        dag_id = dags[0]["dag_id"]

    dag_run_id = f"mcp_e2e_{uuid.uuid4().hex[:12]}"
    created = _as_dict(
        await _call(
            mcp_session,
            "post_dag_run",
            {"dag_id": dag_id, "dag_run_id": dag_run_id},
        )
    )
    assert created.get("dag_id") == dag_id
    assert created.get("dag_run_id") == dag_run_id
    assert created.get("state")

    status = _as_dict(
        await _call(
            mcp_session,
            "get_dag_run",
            {"dag_id": dag_id, "dag_run_id": dag_run_id},
        )
    )
    assert status.get("dag_id") == dag_id
    assert status.get("dag_run_id") == dag_run_id
    assert status.get("state")


@pytest.mark.asyncio
async def test_protocol_variable_create_get_delete(mcp_session: ClientSession) -> None:
    key = f"mcp_e2e_{uuid.uuid4().hex[:12]}"
    value = "protocol-e2e"
    try:
        created = _as_dict(
            await _call(
                mcp_session,
                "create_variable",
                {"key": key, "value": value, "description": "mcp protocol e2e"},
            )
        )
        assert created.get("key") == key
        assert created.get("value") == value

        fetched = _as_dict(await _call(mcp_session, "get_variable", {"key": key}))
        assert fetched.get("key") == key
        assert fetched.get("value") == value

        deleted = await mcp_session.call_tool("delete_variable", {"key": key})
        assert deleted is not None
        missing = await mcp_session.call_tool("get_variable", {"key": key})
        missing_text = str(parse_tool_payload(missing) if not missing.isError else missing)
        assert missing.isError or "404" in missing_text.lower() or "not found" in missing_text.lower()
    finally:
        await mcp_session.call_tool("delete_variable", {"key": key})


@pytest.mark.asyncio
async def test_protocol_connection_create_get_delete(mcp_session: ClientSession) -> None:
    conn_id = f"mcp_e2e_{uuid.uuid4().hex[:12]}"
    try:
        created = _as_dict(
            await _call(
                mcp_session,
                "create_connection",
                {"conn_id": conn_id, "conn_type": "http", "host": "example.com"},
            )
        )
        assert created.get("connection_id") == conn_id or created.get("conn_id") == conn_id

        fetched = _as_dict(await _call(mcp_session, "get_connection", {"conn_id": conn_id}))
        assert fetched.get("connection_id") == conn_id or fetched.get("conn_id") == conn_id
        assert fetched.get("conn_type") == "http"

        deleted = await mcp_session.call_tool("delete_connection", {"conn_id": conn_id})
        assert deleted is not None
        missing = await mcp_session.call_tool("get_connection", {"conn_id": conn_id})
        missing_text = str(parse_tool_payload(missing) if not missing.isError else missing)
        assert missing.isError or "404" in missing_text.lower() or "not found" in missing_text.lower()
    finally:
        await mcp_session.call_tool("delete_connection", {"conn_id": conn_id})


@pytest.mark.asyncio
async def test_protocol_list_pools(mcp_session: ClientSession) -> None:
    payload = _as_dict(await _call(mcp_session, "get_pools"))
    pools = payload.get("pools")
    assert isinstance(pools, list) and pools, f"get_pools returned no pools: {payload}"
    names = {item.get("name") for item in pools if isinstance(item, dict)}
    assert "default_pool" in names
