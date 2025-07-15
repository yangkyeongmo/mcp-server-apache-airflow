from urllib.parse import urljoin

from airflow_client.client import ApiClient, Configuration

from src.envs import (
    AIRFLOW_API_VERSION,
    AIRFLOW_HOST,
    AIRFLOW_PASSWORD,
    AIRFLOW_USERNAME,
)

params = {}

if AIRFLOW_USERNAME:
    params['username'] = AIRFLOW_USERNAME
if AIRFLOW_PASSWORD:
    params['password'] = AIRFLOW_PASSWORD

# Create a configuration and API client
configuration = Configuration(
    host=urljoin(AIRFLOW_HOST, f"/api/{AIRFLOW_API_VERSION}"),
    **params
)
configuration.debug = True
api_client = ApiClient(configuration)
