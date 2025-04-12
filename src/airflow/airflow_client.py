from urllib.parse import urljoin

from airflow_client.client import ApiClient, Configuration

from src.envs import (
    AIRFLOW_API_VERSION,
    AIRFLOW_HOST,
    AIRFLOW_PASSWORD,
    AIRFLOW_USERNAME,
)

# Create a configuration and API client
configuration = Configuration(
    host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    username=AIRFLOW_USERNAME,
    password=AIRFLOW_PASSWORD,
)
api_client = ApiClient(configuration)
