"""Tests for the airflow client authentication module."""

import os
import sys
from unittest.mock import patch

from airflow_client.client import ApiClient


class TestAirflowClientAuthentication:
    """Test cases for airflow client authentication configuration."""

    def test_basic_auth_configuration(self):
        """Test that basic authentication is configured correctly."""
        with patch.dict(
            os.environ,
            {
                "AIRFLOW_HOST": "http://localhost:8080",
                "AIRFLOW_USERNAME": "testuser",
                "AIRFLOW_PASSWORD": "testpass",
                "AIRFLOW_API_VERSION": "v1",
            },
            clear=True,
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import api_client, configuration

            # Verify configuration
            assert configuration.host == "http://localhost:8080/api/v1"
            assert configuration.username == "testuser"
            assert configuration.password == "testpass"
            assert isinstance(api_client, ApiClient)

    def test_jwt_token_auth_configuration(self):
        """Test that JWT token authentication is configured correctly."""
        with patch.dict(
            os.environ,
            {
                "AIRFLOW_HOST": "http://localhost:8080",
                "AIRFLOW_JWT_TOKEN": "test.jwt.token",
                "AIRFLOW_API_VERSION": "v1",
            },
            clear=True,
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import api_client, configuration

            # Verify configuration
            assert configuration.host == "http://localhost:8080/api/v1"
            assert configuration.api_key == {"Authorization": "Bearer test.jwt.token"}
            assert configuration.api_key_prefix == {"Authorization": ""}
            assert isinstance(api_client, ApiClient)

    def test_jwt_token_takes_precedence_over_basic_auth(self):
        """Test that JWT token takes precedence when both auth methods are provided."""
        with patch.dict(
            os.environ,
            {
                "AIRFLOW_HOST": "http://localhost:8080",
                "AIRFLOW_USERNAME": "testuser",
                "AIRFLOW_PASSWORD": "testpass",
                "AIRFLOW_JWT_TOKEN": "test.jwt.token",
                "AIRFLOW_API_VERSION": "v1",
            },
            clear=True,
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import api_client, configuration

            # Verify JWT token is used (not basic auth)
            assert configuration.host == "http://localhost:8080/api/v1"
            assert configuration.api_key == {"Authorization": "Bearer test.jwt.token"}
            assert configuration.api_key_prefix == {"Authorization": ""}
            # Basic auth should not be set when JWT is present
            assert not hasattr(configuration, "username") or configuration.username is None
            assert not hasattr(configuration, "password") or configuration.password is None
            assert isinstance(api_client, ApiClient)

    def test_no_auth_configuration(self):
        """Test that configuration works with no authentication (for testing/development)."""
        with patch.dict(os.environ, {"AIRFLOW_HOST": "http://localhost:8080", "AIRFLOW_API_VERSION": "v1"}, clear=True):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import api_client, configuration

            # Verify configuration
            assert configuration.host == "http://localhost:8080/api/v1"
            # No auth should be set
            assert not hasattr(configuration, "username") or configuration.username is None
            assert not hasattr(configuration, "password") or configuration.password is None
            # api_key might be an empty dict by default, but should not have Authorization
            assert "Authorization" not in getattr(configuration, "api_key", {})
            assert isinstance(api_client, ApiClient)

    def test_environment_variable_parsing(self):
        """Test that environment variables are parsed correctly."""
        with patch.dict(
            os.environ,
            {
                "AIRFLOW_HOST": "https://airflow.example.com:8080/custom",
                "AIRFLOW_JWT_TOKEN": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "AIRFLOW_API_VERSION": "v2",
            },
            clear=True,
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import configuration
            from src.envs import AIRFLOW_API_VERSION, AIRFLOW_HOST, AIRFLOW_JWT_TOKEN

            # Verify environment variables are parsed correctly
            assert AIRFLOW_HOST == "https://airflow.example.com:8080"
            assert AIRFLOW_JWT_TOKEN == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            assert AIRFLOW_API_VERSION == "v2"

            # Verify configuration uses parsed values
            assert configuration.host == "https://airflow.example.com:8080/api/v2"
            assert configuration.api_key == {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
            assert configuration.api_key_prefix == {"Authorization": ""}
