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
