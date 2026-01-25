"""
Airflow API client with support for multiple authentication methods.

Priority: SSO Cookie Auth > JWT Token > Basic Auth
"""

import sys
import threading
import time
from typing import Optional
from urllib.parse import urljoin

from airflow_client.client import ApiClient, Configuration
from airflow_client.client.rest import RESTClientObject
import urllib3

from src.envs import (
    AIRFLOW_API_VERSION,
    AIRFLOW_HEADLESS,
    AIRFLOW_HOST,
    AIRFLOW_JWT_TOKEN,
    AIRFLOW_MAX_COOKIE_AGE_HOURS,
    AIRFLOW_PASSWORD,
    AIRFLOW_SSO_AUTH,
    AIRFLOW_STATE_DIR,
    AIRFLOW_USERNAME,
    AIRFLOW_VERIFY,
)


class SSORESTClient(RESTClientObject):
    """
    Custom REST client that injects SSO cookies into every request.
    Handles automatic cookie refresh on auth failures.
    """

    def __init__(self, configuration, pools_size=4, maxsize=4):
        super().__init__(configuration, pools_size, maxsize)
        self._sso_auth = None
        self._cookie_header: Optional[str] = None
        self._cookie_lock = threading.Lock()
        self._last_refresh = 0.0
        
        # Ensure SSL verification settings are applied to pool manager
        if configuration.verify_ssl is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # Recreate pool manager with SSL verification disabled
            self.pool_manager = urllib3.PoolManager(
                num_pools=pools_size,
                maxsize=maxsize,
                cert_reqs='CERT_NONE',
                assert_hostname=False,
            )

    def set_sso_auth(self, sso_auth):
        """Set the SSO auth handler."""
        self._sso_auth = sso_auth
        self._refresh_cookies()

    def _refresh_cookies(self):
        """Refresh SSO cookies."""
        if self._sso_auth:
            with self._cookie_lock:
                self._cookie_header = self._sso_auth.get_cookie_header()
                self._last_refresh = time.time()

    def request(self, method, url, query_params=None, headers=None,
                body=None, post_params=None, _preload_content=True,
                _request_timeout=None):
        """Override request to inject SSO cookies."""
        if headers is None:
            headers = {}

        # Inject SSO cookie header if available
        if self._cookie_header:
            headers["Cookie"] = self._cookie_header

        try:
            response = super().request(
                method, url, query_params, headers, body, post_params,
                _preload_content, _request_timeout
            )

            # On auth failure, try to refresh cookies and retry once
            if response.status in (401, 403, 302) and self._sso_auth:
                self._refresh_cookies()
                headers["Cookie"] = self._cookie_header
                response = super().request(
                    method, url, query_params, headers, body, post_params,
                    _preload_content, _request_timeout
                )

            return response

        except urllib3.exceptions.HTTPError as e:
            # Try cookie refresh on connection errors that might be auth-related
            if self._sso_auth and self._cookie_header:
                self._refresh_cookies()
                headers["Cookie"] = self._cookie_header
                return super().request(
                    method, url, query_params, headers, body, post_params,
                    _preload_content, _request_timeout
                )
            raise


def _create_sso_client() -> ApiClient:
    """Create an API client with SSO cookie-based authentication."""
    from src.airflow.sso_cookie_auth import AirflowAuthConfig, AirflowCookieAuth

    print("Using SSO cookie-based authentication for Airflow", file=sys.stderr)

    cfg = AirflowAuthConfig(
        base_url=AIRFLOW_HOST,
        state_dir=AIRFLOW_STATE_DIR,
        headless=AIRFLOW_HEADLESS,
        verify=AIRFLOW_VERIFY,
        max_cookie_age_hours=AIRFLOW_MAX_COOKIE_AGE_HOURS,
    )
    sso_auth = AirflowCookieAuth(cfg)

    # Create configuration
    configuration = Configuration(
        host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    )

    # Disable SSL verification if configured
    if AIRFLOW_VERIFY is False:
        configuration.verify_ssl = False
    elif isinstance(AIRFLOW_VERIFY, str):
        configuration.ssl_ca_cert = AIRFLOW_VERIFY

    # Create API client with custom REST client
    client = ApiClient(configuration)

    # Replace the REST client with our SSO-aware version
    sso_rest_client = SSORESTClient(configuration)
    sso_rest_client.set_sso_auth(sso_auth)
    client.rest_client = sso_rest_client

    return client


def _create_jwt_client() -> ApiClient:
    """Create an API client with JWT token authentication."""
    print("Using JWT token authentication for Airflow", file=sys.stderr)

    configuration = Configuration(
        host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    )
    configuration.api_key = {"Authorization": f"Bearer {AIRFLOW_JWT_TOKEN}"}
    configuration.api_key_prefix = {"Authorization": ""}

    return ApiClient(configuration)


def _create_basic_auth_client() -> ApiClient:
    """Create an API client with basic authentication."""
    print("Using basic authentication for Airflow", file=sys.stderr)

    configuration = Configuration(
        host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    )
    configuration.username = AIRFLOW_USERNAME
    configuration.password = AIRFLOW_PASSWORD

    return ApiClient(configuration)


def _create_unauthenticated_client() -> ApiClient:
    """Create an API client without authentication (for testing)."""
    print("WARNING: No authentication configured for Airflow", file=sys.stderr)

    configuration = Configuration(
        host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    )

    return ApiClient(configuration)


def create_api_client() -> ApiClient:
    """
    Create an Airflow API client with the appropriate authentication method.
    
    Priority:
    1. SSO Cookie Auth (if AIRFLOW_SSO_AUTH=true)
    2. JWT Token (if AIRFLOW_JWT_TOKEN is set)
    3. Basic Auth (if AIRFLOW_USERNAME and AIRFLOW_PASSWORD are set)
    4. Unauthenticated (fallback)
    """
    if AIRFLOW_SSO_AUTH:
        return _create_sso_client()
    elif AIRFLOW_JWT_TOKEN:
        return _create_jwt_client()
    elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
        return _create_basic_auth_client()
    else:
        return _create_unauthenticated_client()


# Create the global API client instance
api_client = create_api_client()
