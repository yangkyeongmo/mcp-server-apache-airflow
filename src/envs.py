import os
from urllib.parse import urlparse

# Environment variables for Airflow connection
# AIRFLOW_HOST defaults to localhost for development/testing if not provided
_airflow_host_raw = os.getenv("AIRFLOW_HOST", "http://localhost:8080")
AIRFLOW_HOST = urlparse(_airflow_host_raw)._replace(path="").geturl().rstrip("/")

# Authentication - supports SSO cookie auth, JWT token, and basic auth
# Priority: SSO Cookie > JWT Token > Basic Auth
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
AIRFLOW_JWT_TOKEN = os.getenv("AIRFLOW_JWT_TOKEN")
AIRFLOW_API_VERSION = os.getenv("AIRFLOW_API_VERSION", "v1")

# SSO Cookie-based authentication (for enterprise IdPs like Okta, Azure AD, etc.)
AIRFLOW_SSO_AUTH = os.getenv("AIRFLOW_SSO_AUTH", "false").lower() in ("true", "1", "yes", "on")
AIRFLOW_STATE_DIR = os.getenv("AIRFLOW_STATE_DIR", os.path.expanduser("~/.airflow_cookie_state"))
AIRFLOW_HEADLESS = os.getenv("AIRFLOW_HEADLESS", "false").lower() in ("true", "1", "yes", "on")
AIRFLOW_MAX_COOKIE_AGE_HOURS = int(os.getenv("AIRFLOW_MAX_COOKIE_AGE_HOURS", "24"))

# TLS verification: true, false, or path to CA bundle
_verify_env = os.getenv("AIRFLOW_VERIFY", "true").strip()
if _verify_env.lower() in ("0", "false", "no"):
    AIRFLOW_VERIFY: bool | str = False
elif _verify_env.lower() in ("1", "true", "yes"):
    AIRFLOW_VERIFY = True
else:
    AIRFLOW_VERIFY = _verify_env  # Path to CA bundle

# Environment variable for read-only mode
READ_ONLY = os.getenv("READ_ONLY", "false").lower() in ("true", "1", "yes", "on")
