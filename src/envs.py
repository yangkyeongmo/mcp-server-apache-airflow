import os
from urllib.parse import urlparse

# Environment variables for Airflow connection
# AIRFLOW_HOST defaults to localhost for development/testing if not provided
_airflow_host_raw = os.getenv("AIRFLOW_HOST", "http://localhost:8080")
AIRFLOW_HOST = urlparse(_airflow_host_raw)._replace(path="").geturl().rstrip("/")

# Authentication - supports both basic auth and JWT token auth
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
AIRFLOW_JWT_TOKEN = os.getenv("AIRFLOW_JWT_TOKEN")
AIRFLOW_API_VERSION = os.getenv("AIRFLOW_API_VERSION", "v1")

# Environment variable for read-only mode
READ_ONLY = os.getenv("READ_ONLY", "false").lower() in ("true", "1", "yes", "on")
