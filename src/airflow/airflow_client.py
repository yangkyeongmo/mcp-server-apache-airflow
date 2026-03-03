import subprocess
import threading
from typing import Any
from urllib.parse import urljoin

from airflow_client.client import ApiClient, Configuration
from airflow_client.client.exceptions import ApiException

from src.envs import (
    AIRFLOW_API_VERSION,
    AIRFLOW_HOST,
    AIRFLOW_JWT_TOKEN,
    AIRFLOW_JWT_TOKEN_REFRESH_COMMAND,
    AIRFLOW_PASSWORD,
    AIRFLOW_USERNAME,
)

# Global variable to store current JWT token
_current_jwt_token: str | None = AIRFLOW_JWT_TOKEN


def _execute_token_refresh_command() -> str:
    """
    Run the configured token refresh command and return the new token.

    Used both when building initial configuration (no token provided) and when
    TokenRefreshApiClient refreshes on 401.

    Raises:
        RuntimeError: If the command execution fails or returns non-zero exit code.
    """
    if not AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
        raise RuntimeError("No token refresh command configured")

    try:
        result = subprocess.run(
            AIRFLOW_JWT_TOKEN_REFRESH_COMMAND,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Token refresh command failed with exit code {result.returncode}: {result.stderr}"
            )

        token = result.stdout.strip()
        if not token:
            raise RuntimeError("Token refresh command returned empty token")

        return token

    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Token refresh command timed out after 30 seconds") from e
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Failed to execute token refresh command: {str(e)}") from e


class TokenRefreshApiClient(ApiClient):
    """
    Custom ApiClient that automatically refreshes JWT tokens on 401 Unauthorized errors.

    This wrapper extends the standard ApiClient to intercept 401 errors,
    execute the token refresh command, and retry the request with the new token.
    """

    _refresh_lock = threading.Lock()

    def call_api(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute API call with automatic token refresh on 401 errors.

        Returns:
            API response.

        Raises:
            ApiException: For non-401 errors or if token refresh fails.
        """
        try:
            return super().call_api(*args, **kwargs)
        except ApiException as e:
            # Check if it's an authorization error and we have a refresh command
            if e.status == 401 and AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
                try:
                    self._refresh_token(_current_jwt_token)
                    # Retry the request with the new token
                    return super().call_api(*args, **kwargs)
                except Exception as refresh_error:  # noqa: BLE001
                    raise e from refresh_error
            raise

    def _update_token(self, new_token: str) -> None:
        """
        Update the JWT token in the configuration and API client.
        """
        global _current_jwt_token, api_client

        _current_jwt_token = new_token
        configuration.api_key = {"Authorization": f"{new_token}"}
        configuration.api_key_prefix = {"Authorization": "Bearer"}
        api_client.default_headers["Authorization"] = configuration.get_api_key_with_prefix("Authorization")

    def _refresh_token(self, old_token: str | None) -> None:
        """
        Refresh the JWT token by executing the refresh command and updating the configuration.

        Uses a lock to prevent multiple simultaneous refresh operations when multiple threads
        receive 401 errors at the same time. If another thread already refreshed the token,
        this function will skip the refresh to avoid redundant command executions.
        """
        with self._refresh_lock:
            # If token changed (another thread already refreshed it), skip
            if _current_jwt_token != old_token:
                return
            new_token = _execute_token_refresh_command()
            self._update_token(new_token)


def build_configuration() -> Configuration:
    """
    Build a configured Airflow API client Configuration.

    The configuration includes:
    - API host constructed from AIRFLOW_HOST and AIRFLOW_API_VERSION
    - Authentication based on environment variables, with the following precedence:
      1. Static JWT token via AIRFLOW_JWT_TOKEN
      2. JWT token obtained via AIRFLOW_JWT_TOKEN_REFRESH_COMMAND
      3. Basic auth via AIRFLOW_USERNAME and AIRFLOW_PASSWORD
    """
    global _current_jwt_token

    config = Configuration(
        host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    )

    # Initialize authentication on the configuration
    if _current_jwt_token:
        # JWT token provided, use it
        config.api_key = {"Authorization": f"{_current_jwt_token}"}
        config.api_key_prefix = {"Authorization": "Bearer"}
    elif AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
        # No token provided but refresh command available, execute it to get initial token.
        _current_jwt_token = _execute_token_refresh_command()
        config.api_key = {"Authorization": f"{_current_jwt_token}"}
        config.api_key_prefix = {"Authorization": "Bearer"}
    elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
        # Fallback to basic auth
        config.username = AIRFLOW_USERNAME
        config.password = AIRFLOW_PASSWORD

    return config


def create_airflow_api_client(config: Configuration | None = None) -> ApiClient:
    """
    Create a configured Airflow ApiClient instance.

    The client:
    - Uses TokenRefreshApiClient when AIRFLOW_JWT_TOKEN_REFRESH_COMMAND is configured
    - Uses ApiClient otherwise
    - Sets the Authorization header when a JWT token is available
    """
    global _current_jwt_token

    configuration_to_use = config or build_configuration()

    if AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
        client: ApiClient = TokenRefreshApiClient(configuration_to_use)
    else:
        client = ApiClient(configuration_to_use)

    # JWT/Bearer auth requires manual header setup because auth_settings() in apache-airflow-client 2.x
    # only supports Basic authentication.
    # If ever updated to apache-airflow-client 3.x it's the other way around, JWT/Bearer is natively
    # supported through "access_token", and Basic auth requires manual header.
    if _current_jwt_token:
        client.default_headers["Authorization"] = configuration_to_use.get_api_key_with_prefix("Authorization")

    return client


# Module-level configuration and API client for convenience and backwards compatibility.
configuration = build_configuration()
api_client = create_airflow_api_client(configuration)
