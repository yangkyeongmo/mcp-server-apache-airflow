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
    host=f"{AIRFLOW_HOST}/api/{AIRFLOW_API_VERSION}",
)

# Set up authentication - prefer JWT token if available, fallback to basic auth
if AIRFLOW_JWT_TOKEN:
    configuration.api_key = {"Authorization": f"{AIRFLOW_JWT_TOKEN}"}
    configuration.api_key_prefix = {"Authorization": "Bearer"}
elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
    configuration.username = AIRFLOW_USERNAME
    configuration.password = AIRFLOW_PASSWORD

api_client = ApiClient(configuration)

# JWT/Bearer auth requires manual header setup because auth_settings() in apache-airflow-client 2.x
# only supports Basic authentication.
# If ever updated to apache-airflow-client 3.x it's the other way around, JWT/Bearer is natively
# supported through "access_token", and Basic auth requires manual header.
if AIRFLOW_JWT_TOKEN:
    api_client.default_headers["Authorization"] = configuration.get_api_key_with_prefix("Authorization")
