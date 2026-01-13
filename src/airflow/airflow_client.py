from base64 import b64encode
from urllib.parse import urljoin

from airflow_client.client import ApiClient, Configuration

from src.envs import (
    AIRFLOW_API_VERSION,
    AIRFLOW_HOST,
    AIRFLOW_JWT_TOKEN,
    AIRFLOW_PASSWORD,
    AIRFLOW_USERNAME,
)

# Create a configuration and API client
configuration = Configuration(
    host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
)

# Set up authentication - prefer JWT token if available, fallback to basic auth
if AIRFLOW_JWT_TOKEN:
    configuration.api_key = {"Authorization": f"Bearer {AIRFLOW_JWT_TOKEN}"}
    configuration.api_key_prefix = {"Authorization": ""}
elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
    configuration.username = AIRFLOW_USERNAME
    configuration.password = AIRFLOW_PASSWORD

api_client = ApiClient(configuration)

# Fallback: If configuration doesn't produce auth_settings, set headers directly.
# This is needed for some versions of apache-airflow-client which don't apply
# api_key or basic auth to requests properly.
if not configuration.auth_settings():
    if AIRFLOW_JWT_TOKEN:
        api_client.default_headers["Authorization"] = f"Bearer {AIRFLOW_JWT_TOKEN}"
    elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
        credentials = b64encode(f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode()).decode()
        api_client.default_headers["Authorization"] = f"Basic {credentials}"
