import os
from urllib.parse import urlparse

AIRFLOW_HOST = urlparse(os.getenv("AIRFLOW_HOST"))._replace(path="").geturl().rstrip("/")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
AIRFLOW_API_VERSION = os.getenv("AIRFLOW_API_VERSION", "v1")
