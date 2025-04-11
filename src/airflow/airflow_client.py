from airflow_client.client import ApiClient, Configuration

from src.envs import AIRFLOW_HOST, AIRFLOW_PASSWORD, AIRFLOW_USERNAME

# Create a configuration and API client
configuration = Configuration(
    host=f"{AIRFLOW_HOST}/api/v1",
    username=AIRFLOW_USERNAME,
    password=AIRFLOW_PASSWORD,
)
api_client = ApiClient(configuration)
