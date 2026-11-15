"""Fixtures for live Airflow integration tests."""

from __future__ import annotations

import os
from collections.abc import Iterator

import httpx
import pytest


def pytest_configure(config: pytest.Config) -> None:
    os.environ.setdefault("AIRFLOW_HOST", "http://127.0.0.1:8080")
    os.environ.setdefault("AIRFLOW_USERNAME", "airflow")
    os.environ.setdefault("AIRFLOW_PASSWORD", "airflow")
    os.environ.setdefault("AIRFLOW_API_VERSION", "v1")


@pytest.fixture(scope="session")
def airflow_base_url() -> str:
    return os.environ.get("AIRFLOW_HOST", "http://127.0.0.1:8080").rstrip("/")


@pytest.fixture(scope="session")
def live_airflow(airflow_base_url: str) -> Iterator[str]:
    """Fail in CI when Airflow 2.x is down; skip locally if nothing is listening."""
    if os.environ.get("AIRFLOW_MAJOR") == "3":
        pytest.skip(
            "Airflow 3.x integration is blocked by apache-airflow-client>=2.7.0,<3 "
            "(stable REST client speaks /api/v1 only)."
        )

    username = os.environ.get("AIRFLOW_USERNAME", "airflow")
    password = os.environ.get("AIRFLOW_PASSWORD", "airflow")
    health_url = f"{airflow_base_url}/api/v1/health"
    try:
        response = httpx.get(health_url, auth=(username, password), timeout=5.0)
        if response.status_code in {401, 403}:
            response = httpx.get(health_url, timeout=5.0)
        response.raise_for_status()
    except Exception as exc:
        in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
        require_live = os.environ.get("AIRFLOW_INTEGRATION_REQUIRED") == "1"
        if in_ci or require_live:
            raise RuntimeError(f"Airflow health check failed at {health_url}: {exc}") from exc
        pytest.skip(f"Live Airflow is not available at {health_url}: {exc}")
    yield airflow_base_url
