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

# Global token; updated on refresh. Synced to configuration and api_client below.
_current_jwt_token: str | None = AIRFLOW_JWT_TOKEN


def _execute_token_refresh_command() -> str:
    """
    Run the configured token refresh command and return the new token.

    Raises:
        RuntimeError: If the command fails or returns non-zero exit code.
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
    ApiClient that refreshes JWT on 401 and retries. Uses module-level
    _current_jwt_token, configuration, and api_client.
    """

    _refresh_lock = threading.Lock()

    def call_api(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return super().call_api(*args, **kwargs)
        except ApiException as e:
            if e.status == 401 and AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
                try:
                    self._refresh_token(_current_jwt_token)
                    return super().call_api(*args, **kwargs)
                except Exception as refresh_error:  # noqa: BLE001
                    raise e from refresh_error
            raise

    def _refresh_token(self, old_token: str | None) -> None:
        global _current_jwt_token, configuration, api_client
        with self._refresh_lock:
            if _current_jwt_token != old_token:
                return
            new_token = _execute_token_refresh_command()
            _current_jwt_token = new_token
            configuration.api_key = {"Authorization": new_token}
            configuration.api_key_prefix = {"Authorization": "Bearer"}
            api_client.default_headers["Authorization"] = configuration.get_api_key_with_prefix("Authorization")


def build_configuration() -> Configuration:
    """
    Build Configuration from env: host, then auth precedence
    (JWT token, refresh command, basic auth).
    """
    global _current_jwt_token

    config = Configuration(
        host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    )
    if _current_jwt_token:
        config.api_key = {"Authorization": _current_jwt_token}
        config.api_key_prefix = {"Authorization": "Bearer"}
    elif AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
        _current_jwt_token = _execute_token_refresh_command()
        config.api_key = {"Authorization": _current_jwt_token}
        config.api_key_prefix = {"Authorization": "Bearer"}
    elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
        config.username = AIRFLOW_USERNAME
        config.password = AIRFLOW_PASSWORD
    return config


def create_airflow_api_client(config: Configuration | None = None) -> ApiClient:
    """
    Create configured ApiClient; use TokenRefreshApiClient when refresh command is set.
    """
    configuration_to_use = config or build_configuration()

    if AIRFLOW_JWT_TOKEN_REFRESH_COMMAND:
        client = TokenRefreshApiClient(configuration_to_use)
    else:
        client = ApiClient(configuration_to_use)

    if _current_jwt_token:
        client.default_headers["Authorization"] = configuration_to_use.get_api_key_with_prefix("Authorization")
    return client


configuration = build_configuration()
api_client = create_airflow_api_client(configuration)
