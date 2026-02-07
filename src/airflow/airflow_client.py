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

# Thread lock for token refresh to prevent concurrent refresh operations
_token_refresh_lock = threading.Lock()

# Create a configuration and API client
configuration = Configuration(
    host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
)

# Global variable to store current JWT token
_current_jwt_token: str | None = AIRFLOW_JWT_TOKEN


def execute_token_refresh_command() -> str:
    """
    Execute the token refresh command and return the new token.

    Returns:
        The new JWT token as a string.

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
            raise RuntimeError(f"Token refresh command failed with exit code {result.returncode}: {result.stderr}")

        token = result.stdout.strip()
        if not token:
            raise RuntimeError("Token refresh command returned empty token")

        return token

    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Token refresh command timed out after 30 seconds") from e
    except Exception as e:
        raise RuntimeError(f"Failed to execute token refresh command: {str(e)}") from e


def update_token(new_token: str) -> None:
    """
    Update the JWT token in the configuration and API client.

    Args:
        new_token: The new JWT token to use.
    """
    global _current_jwt_token

    with _token_refresh_lock:
        _current_jwt_token = new_token
        configuration.api_key = {"Authorization": f"{new_token}"}
        configuration.api_key_prefix = {"Authorization": "Bearer"}
        api_client.default_headers["Authorization"] = configuration.get_api_key_with_prefix("Authorization")


def refresh_token() -> None:
    """
    Refresh the JWT token by executing the refresh command and updating the configuration.

    Raises:
        RuntimeError: If token refresh fails or no refresh command is configured.
    """
    new_token = execute_token_refresh_command()
    update_token(new_token)


class TokenRefreshApiClient(ApiClient):
    """
    Custom ApiClient that automatically refreshes JWT tokens on 401 Unauthorized errors.

    This wrapper extends the standard ApiClient to intercept 401 errors,
    execute the token refresh command, and retry the request with the new token.
    """

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
                    refresh_token()
                    # Retry the request with the new token
                    return super().call_api(*args, **kwargs)
                except Exception as refresh_error:
                    raise e from refresh_error
            raise


# Initialize JWT token
if _current_jwt_token:
    # JWT token provided, use it
    configuration.api_key = {"Authorization": f"{_current_jwt_token}"}
    configuration.api_key_prefix = {"Authorization": "Bearer"}
elif AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
    # No token provided but refresh command available, execute it to get initial token
    _current_jwt_token = execute_token_refresh_command()
    configuration.api_key = {"Authorization": f"{_current_jwt_token}"}
    configuration.api_key_prefix = {"Authorization": "Bearer"}
elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
    # Fallback to basic auth
    configuration.username = AIRFLOW_USERNAME
    configuration.password = AIRFLOW_PASSWORD

# Create API client with automatic token refresh if refresh command is configured
if AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
    api_client = TokenRefreshApiClient(configuration)
else:
    api_client = ApiClient(configuration)

# JWT/Bearer auth requires manual header setup because auth_settings() in apache-airflow-client 2.x
# only supports Basic authentication.
# If ever updated to apache-airflow-client 3.x it's the other way around, JWT/Bearer is natively
# supported through "access_token", and Basic auth requires manual header.
if _current_jwt_token:
    api_client.default_headers["Authorization"] = configuration.get_api_key_with_prefix("Authorization")
