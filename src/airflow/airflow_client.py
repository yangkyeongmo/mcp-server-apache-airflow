from airflow_client.client import ApiClient, Configuration

from src.envs import AIRFLOW_HOST, AIRFLOW_PASSWORD, AIRFLOW_USERNAME

# Create a configuration and API client
configuration = Configuration(
    host=AIRFLOW_HOST,
    username=AIRFLOW_USERNAME,
    password=AIRFLOW_PASSWORD,
)
api_client = ApiClient(configuration)
