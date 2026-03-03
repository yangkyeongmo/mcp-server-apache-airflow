import os
from urllib.parse import urlparse

import requests

# Environment variables for Airflow connection
_airflow_host_raw = os.getenv("AIRFLOW_HOST", "http://localhost:8080")
AIRFLOW_HOST = urlparse(_airflow_host_raw)._replace(path="").geturl().rstrip("/")

# Authentication - supports both basic auth and JWT token auth
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
AIRFLOW_JWT_TOKEN = os.getenv("AIRFLOW_JWT_TOKEN")

# Environment variable for read-only mode
READ_ONLY = os.getenv("READ_ONLY", "false").lower() in ("true", "1", "yes", "on")

# -----------------------------
# Auto-detect Airflow API version
# -----------------------------


def detect_api_version():
    headers = {}

    if AIRFLOW_JWT_TOKEN:
        headers["Authorization"] = f"Bearer {AIRFLOW_JWT_TOKEN}"

    auth = None
    if AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
        auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)

    for version in ["v2", "v1"]:  # Try v2 first (Airflow 3)
        try:
            response = requests.get(
                f"{AIRFLOW_HOST}/api/{version}/version",
                headers=headers,
                auth=auth,
                timeout=3,
            )
            if response.status_code == 200:
                return version
        except requests.RequestException:
            pass

    # Default fallback
    return "v1"


# If user explicitly sets version, respect it
AIRFLOW_API_VERSION = os.getenv("AIRFLOW_API_VERSION")

if not AIRFLOW_API_VERSION:
    AIRFLOW_API_VERSION = detect_api_version()
