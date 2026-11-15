"""Session fixtures for live Airflow integration tests."""

from __future__ import annotations

import os
import time
from urllib.parse import urljoin

import pytest

DEFAULT_HOST = "http://127.0.0.1:8080"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("AIRFLOW_INTEGRATION") == "1":
        return
    skip = pytest.mark.skip(reason="Set AIRFLOW_INTEGRATION=1 against a running Airflow to run live tests")
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def airflow_connection() -> dict[str, str]:
    host = os.environ.get("AIRFLOW_HOST", DEFAULT_HOST).rstrip("/")
    return {
        "host": host,
        "username": os.environ.get("AIRFLOW_USERNAME", "airflow"),
        "password": os.environ.get("AIRFLOW_PASSWORD", "airflow"),
        "api_version": os.environ.get("AIRFLOW_API_VERSION", "v1"),
    }


@pytest.fixture(scope="session", autouse=True)
def wait_for_airflow(airflow_connection: dict[str, str]) -> None:
    if os.environ.get("AIRFLOW_INTEGRATION") != "1":
        return

    import httpx

    health_url = urljoin(airflow_connection["host"] + "/", "api/v1/health")
    deadline = time.time() + 180
    last_error = "no attempt"
    while time.time() < deadline:
        try:
            response = httpx.get(health_url, timeout=5.0)
            if response.status_code == 200:
                break
            last_error = f"HTTP {response.status_code}"
        except Exception as exc:  # network/HTTP until Airflow is up
            last_error = str(exc)
        time.sleep(2)
    else:
        pytest.fail(f"Airflow at {health_url} did not become healthy: {last_error}")

    from src.airflow.airflow_client import api_client, configuration

    configuration.host = urljoin(airflow_connection["host"] + "/", f"api/{airflow_connection['api_version']}")
    configuration.username = airflow_connection["username"]
    configuration.password = airflow_connection["password"]
    # Drop any leftover JWT header from other tests in this process.
    api_client.default_headers.pop("Authorization", None)
