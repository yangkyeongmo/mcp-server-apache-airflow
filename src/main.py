import click

from src.airflow.config import get_all_functions as get_config_functions
from src.airflow.connection import get_all_functions as get_connection_functions
from src.airflow.dag import get_all_functions as get_dag_functions
from src.airflow.dagrun import get_all_functions as get_dagrun_functions
from src.airflow.dagstats import get_all_functions as get_dagstats_functions
from src.airflow.dataset import get_all_functions as get_dataset_functions
from src.airflow.eventlog import get_all_functions as get_eventlog_functions
from src.airflow.importerror import get_all_functions as get_importerror_functions
from src.airflow.monitoring import get_all_functions as get_monitoring_functions
from src.airflow.plugin import get_all_functions as get_plugin_functions
from src.airflow.pool import get_all_functions as get_pool_functions
from src.airflow.taskinstance import get_all_functions as get_taskinstance_functions
from src.airflow.variable import get_all_functions as get_variable_functions
from src.airflow.xcom import get_all_functions as get_xcom_functions
from src.enums import APIType

APITYPE_TO_FUNCTIONS = {
    APIType.CONFIG: get_config_functions,
    APIType.CONNECTION: get_connection_functions,
    APIType.DAG: get_dag_functions,
    APIType.DAGRUN: get_dagrun_functions,
    APIType.DAGSTATS: get_dagstats_functions,
    APIType.DATASET: get_dataset_functions,
    APIType.EVENTLOG: get_eventlog_functions,
    APIType.IMPORTERROR: get_importerror_functions,
    APIType.MONITORING: get_monitoring_functions,
    APIType.PLUGIN: get_plugin_functions,
    APIType.POOL: get_pool_functions,
    APIType.TASKINSTANCE: get_taskinstance_functions,
    APIType.VARIABLE: get_variable_functions,
    APIType.XCOM: get_xcom_functions,
}


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.option(
    "--apis",
    type=click.Choice([api.value for api in APIType]),
    default=[api.value for api in APIType],
    multiple=True,
    help="APIs to run, default is all",
)
def main(transport: str, apis: list[str]) -> None:
    from src.server import app

    for api in apis:
        get_function = APITYPE_TO_FUNCTIONS[APIType(api)]
        try:
            functions = get_function()
        except NotImplementedError:
            continue

        for fn, name, description in functions:
            app.add_tool(fn, name=name, description=description)

    if transport == "sse":
        app.run(transport="sse")
    else:
        app.run(transport="stdio")
