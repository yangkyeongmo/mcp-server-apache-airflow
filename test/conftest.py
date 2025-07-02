"""
Pytest configuration and shared fixtures for the test suite.

This file contains shared test fixtures, configurations, and utilities
that can be used across all test modules.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

# Add the src directory to the Python path for imports during testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_fastmcp_app():
    """Create a mock FastMCP app instance for testing."""
    mock_app = MagicMock()
    mock_app.name = "test-app"
    mock_app.add_tool = MagicMock()
    mock_app.run = MagicMock()
    return mock_app


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def api_function_sample():
    """Sample API function for testing function registration."""
    def sample_api_function(param: str) -> str:
        return f"Sample response: {param}"
    
    return (sample_api_function, "sample_function", "Sample function for testing")


@pytest.fixture
def mock_api_functions():
    """Mock API functions list for testing."""
    return [
        (lambda x: f"func1: {x}", "function_1", "First test function"),
        (lambda x: f"func2: {x}", "function_2", "Second test function"),
        (lambda x: f"func3: {x}", "function_3", "Third test function"),
    ]


@pytest.fixture
def mock_environment_vars(monkeypatch):
    """Mock environment variables for testing."""
    test_env_vars = {
        "AIRFLOW_HOST": "http://localhost:8080",
        "AIRFLOW_USERNAME": "test_user",
        "AIRFLOW_PASSWORD": "test_password",
        "AIRFLOW_API_VERSION": "v1",
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)
    
    return test_env_vars 