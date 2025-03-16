from mcp.server.fastmcp import FastMCP

from src.airflow.dag import get_all_functions as get_dag_functions
from src.airflow.dagrun import get_all_functions as get_dagrun_functions
from src.airflow.importerror import get_all_functions as get_importerror_functions
from src.airflow.monitoring import get_all_functions as get_monitoring_functions
from src.airflow.taskinstance import get_all_functions as get_taskinstance_functions
from src.airflow.variable import get_all_functions as get_variable_functions


app = FastMCP("mcp-apache-airflow")

for fn, name, description in get_dag_functions():
    app.add_tool(fn, name=name, description=description)
for fn, name, description in get_dagrun_functions():
    app.add_tool(fn, name=name, description=description)
for fn, name, description in get_importerror_functions():
    app.add_tool(fn, name=name, description=description)
for fn, name, description in get_monitoring_functions():
    app.add_tool(fn, name=name, description=description)
for fn, name, description in get_taskinstance_functions():
    app.add_tool(fn, name=name, description=description)
for fn, name, description in get_variable_functions():
    app.add_tool(fn, name=name, description=description)
