from airflow_client.client import ApiClient, Configuration

from src.envs import (
    AIRFLOW_HOST,
    AIRFLOW_PASSWORD,
    AIRFLOW_USERNAME,
    AIRFLOW_API_VERSION,
)

# Create a configuration and API client
configuration = Configuration(
    host=f"{AIRFLOW_HOST}/api/{AIRFLOW_API_VERSION}",
    username=AIRFLOW_USERNAME,
    password=AIRFLOW_PASSWORD,
)
api_client = ApiClient(configuration)
