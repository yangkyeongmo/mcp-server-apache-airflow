"""Tests for the airflow client authentication module."""

import base64
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

from airflow_client.client import ApiClient
from airflow_client.client.exceptions import ApiException


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
            from src.airflow.airflow_client import api_client, configuration, create_airflow_api_client

            # Verify configuration
            assert configuration.host == "http://localhost:8080/api/v1"
            assert configuration.username == "testuser"
            assert configuration.password == "testpass"
            assert isinstance(api_client, ApiClient)
            # Factory should produce a client equivalent to the module-level one
            factory_client = create_airflow_api_client()
            assert isinstance(factory_client, ApiClient)

            # No manual header needed - auth_settings() handles Basic auth in v2.x
            assert "Authorization" not in api_client.default_headers
            # Verify auth_settings() returns the correct Basic auth format
            auth_settings = configuration.auth_settings()
            assert "Basic" in auth_settings
            assert auth_settings["Basic"]["key"] == "Authorization"
            # Verify the value format: "Basic <base64(username:password)>"
            auth_value = auth_settings["Basic"]["value"]
            assert auth_value.startswith("Basic ")
            decoded_credentials = base64.b64decode(auth_value.split(" ")[1]).decode()
            assert decoded_credentials == "testuser:testpass"

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
            from src.airflow.airflow_client import api_client, configuration, create_airflow_api_client

            # Verify configuration
            assert configuration.host == "http://localhost:8080/api/v1"
            assert configuration.api_key == {"Authorization": "test.jwt.token"}
            assert configuration.api_key_prefix == {"Authorization": "Bearer"}
            assert isinstance(api_client, ApiClient)
            # Factory should produce a client with the same JWT configuration
            factory_client = create_airflow_api_client()
            assert isinstance(factory_client, ApiClient)

            # auth_settings() is empty for JWT in v2.x (api_key is dead code in library)
            assert configuration.auth_settings() == {}
            # JWT auth requires manual header in v2.x (api_key/auth_settings doesn't support Bearer)
            assert api_client.default_headers["Authorization"] == "Bearer test.jwt.token"

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
            from src.airflow.airflow_client import api_client, configuration, create_airflow_api_client

            # Verify JWT token is used (not basic auth)
            assert configuration.host == "http://localhost:8080/api/v1"
            assert configuration.api_key == {"Authorization": "test.jwt.token"}
            assert configuration.api_key_prefix == {"Authorization": "Bearer"}
            # Basic auth should not be set when JWT is present
            assert not hasattr(configuration, "username") or configuration.username is None
            assert not hasattr(configuration, "password") or configuration.password is None
            assert isinstance(api_client, ApiClient)
            # Factory should honour the same precedence rules
            factory_client = create_airflow_api_client()
            assert isinstance(factory_client, ApiClient)

    def test_no_auth_configuration(self):
        """Test that configuration works with no authentication (for testing/development)."""
        with patch.dict(os.environ, {"AIRFLOW_HOST": "http://localhost:8080", "AIRFLOW_API_VERSION": "v1"}, clear=True):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import api_client, configuration, create_airflow_api_client

            # Verify configuration
            assert configuration.host == "http://localhost:8080/api/v1"
            # No auth should be set
            assert not hasattr(configuration, "username") or configuration.username is None
            assert not hasattr(configuration, "password") or configuration.password is None
            # api_key might be an empty dict by default, but should not have Authorization
            assert "Authorization" not in getattr(configuration, "api_key", {})
            assert isinstance(api_client, ApiClient)
            # Factory should also create an unauthenticated client
            factory_client = create_airflow_api_client()
            assert isinstance(factory_client, ApiClient)

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
            assert configuration.api_key == {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
            assert configuration.api_key_prefix == {"Authorization": "Bearer"}

    def test_jwt_token_refresh_command_with_initial_token(self):
        """Test JWT token refresh command configuration with initial token."""
        with patch.dict(
            os.environ,
            {
                "AIRFLOW_HOST": "http://localhost:8080",
                "AIRFLOW_JWT_TOKEN": "initial.jwt.token",
                "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "echo new.jwt.token",
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

            # Verify initial token is used
            assert configuration.api_key == {"Authorization": "initial.jwt.token"}
            assert api_client.default_headers["Authorization"] == "Bearer initial.jwt.token"

    def test_jwt_token_refresh_command_without_initial_token(self):
        """Test JWT token refresh command obtains initial token when none provided."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "generated.jwt.token\n"
        mock_result.stderr = ""

        with (
            patch.dict(
                os.environ,
                {
                    "AIRFLOW_HOST": "http://localhost:8080",
                    "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "echo generated.jwt.token",
                    "AIRFLOW_API_VERSION": "v1",
                },
                clear=True,
            ),
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Re-import after setting environment
            from src.airflow.airflow_client import api_client, configuration

            # Verify the refresh command was called
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "echo generated.jwt.token" in str(call_args)

            # Verify the token from command is used
            assert configuration.api_key == {"Authorization": "generated.jwt.token"}
            assert api_client.default_headers["Authorization"] == "Bearer generated.jwt.token"

    def test_execute_token_refresh_command_failure(self):
        """Test handling of failed token refresh command (non-zero exit code)."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Authentication failed"

        with (
            patch.dict(
                os.environ,
                {
                    "AIRFLOW_HOST": "http://localhost:8080",
                    "AIRFLOW_JWT_TOKEN": "initial.token",
                    "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "echo test-token",
                    "AIRFLOW_API_VERSION": "v1",
                },
                clear=True,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            from src.airflow.airflow_client import _execute_token_refresh_command

            # Execute the refresh command and expect an error
            try:
                _execute_token_refresh_command()
                raise AssertionError("Should have raised RuntimeError")
            except RuntimeError as e:
                assert "failed with exit code 1" in str(e)

    def test_execute_token_refresh_command_timeout(self):
        """Test handling of token refresh command timeout."""
        with (
            patch.dict(
                os.environ,
                {
                    "AIRFLOW_HOST": "http://localhost:8080",
                    "AIRFLOW_JWT_TOKEN": "initial.token",
                    "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "echo test-token",
                    "AIRFLOW_API_VERSION": "v1",
                },
                clear=True,
            ),
            patch("subprocess.run", side_effect=subprocess.TimeoutExpired("echo test-token", 30)),
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            from src.airflow.airflow_client import _execute_token_refresh_command

            # Execute the refresh command and expect a timeout error
            try:
                _execute_token_refresh_command()
                raise AssertionError("Should have raised RuntimeError")
            except RuntimeError as e:
                assert "timed out" in str(e)

    def test_api_call_with_token_refresh_on_401(self):
        """Test that API calls automatically refresh token on 401 errors."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "refreshed.token\n"
        mock_result.stderr = ""

        with (
            patch.dict(
                os.environ,
                {
                    "AIRFLOW_HOST": "http://localhost:8080",
                    "AIRFLOW_JWT_TOKEN": "expired.token",
                    "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "echo refreshed.token",
                    "AIRFLOW_API_VERSION": "v1",
                },
                clear=True,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            from src.airflow.airflow_client import TokenRefreshApiClient, api_client

            # Verify we got the TokenRefreshApiClient
            assert isinstance(api_client, TokenRefreshApiClient)

            # Mock the parent class call_api to fail with 401 first, then succeed
            call_count = 0

            def mock_call_api(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    # First call fails with 401
                    raise ApiException(status=401, reason="Unauthorized")
                # Second call (after refresh) succeeds
                return {"success": True}

            # Patch ApiClient.call_api (the parent class method)
            with patch.object(ApiClient, "call_api", side_effect=mock_call_api):
                # Call through our wrapper which should handle 401 and retry
                result = api_client.call_api()

                # Verify the retry worked
                assert result == {"success": True}
                assert call_count == 2  # Should have retried once

    def test_api_call_with_token_refresh_failure_on_401(self):
        """Test that refresh failures are properly propagated when handling 401 errors."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"

        with (
            patch.dict(
                os.environ,
                {
                    "AIRFLOW_HOST": "http://localhost:8080",
                    "AIRFLOW_JWT_TOKEN": "expired.token",
                    "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "echo refreshed.token",
                    "AIRFLOW_API_VERSION": "v1",
                },
                clear=True,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            # Clear any cached modules
            modules_to_clear = ["src.envs", "src.airflow.airflow_client"]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            from src.airflow.airflow_client import TokenRefreshApiClient, api_client

            # Verify we got the TokenRefreshApiClient
            assert isinstance(api_client, TokenRefreshApiClient)

            # Mock the parent class call_api to always fail with 401
            def mock_call_api(*args, **kwargs):
                raise ApiException(status=401, reason="Unauthorized")

            # Patch ApiClient.call_api (the parent class method)
            with patch.object(ApiClient, "call_api", side_effect=mock_call_api):
                # Call should fail with 401, attempt refresh (which fails), then raise original 401
                try:
                    api_client.call_api()
                    raise AssertionError("Should have raised ApiException")
                except ApiException as e:
                    # Verify original 401 error is raised
                    assert e.status == 401
                    # Verify it has the refresh error chained
                    assert e.__cause__ is not None
                    assert isinstance(e.__cause__, RuntimeError)
                    assert "failed with exit code 1" in str(e.__cause__)
