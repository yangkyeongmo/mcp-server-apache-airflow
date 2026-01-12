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

# Set up basic auth if provided (and no JWT token)
if not AIRFLOW_JWT_TOKEN and AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
    configuration.username = AIRFLOW_USERNAME
    configuration.password = AIRFLOW_PASSWORD

api_client = ApiClient(configuration)

# Set JWT token via default headers - this is required because
# configuration.api_key doesn't work properly with apache-airflow-client
if AIRFLOW_JWT_TOKEN:
    api_client.default_headers["Authorization"] = f"Bearer {AIRFLOW_JWT_TOKEN}"
