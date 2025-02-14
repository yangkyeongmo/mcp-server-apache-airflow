import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server

from src import airflow

COMMANDS = [
    "list_dags",
    "get_dag",
    "pause_dag",
    "unpause_dag",
    "trigger_dag",
    "get_dag_runs",
    "get_dag_tasks",
    "get_task_instance",
    "list_task_instances",
    "get_import_error",
    "list_import_errors",
    "get_health",
    "get_version",
]


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-website-fetcher")

    @app.call_tool()
    async def fetch_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name not in COMMANDS:
            raise ValueError(f"Unknown tool: {name}")
        if name == "list_dags":
            return await airflow.fetch_dags(
                limit=arguments.get("limit"),
                offset=arguments.get("offset"),
                order_by=arguments.get("order_by"),
                tags=arguments.get("tags"),
                only_active=arguments.get("only_active"),
                paused=arguments.get("paused"),
                dag_id_pattern=arguments.get("dag_id_pattern"),
            )
        elif name == "get_dag":
            if "dag_id" not in arguments:
                raise ValueError("Missing required argument 'dag_id'")
            return await airflow.get_dag(arguments["dag_id"])
        elif name == "pause_dag":
            if "dag_id" not in arguments:
                raise ValueError("Missing required argument 'dag_id'")
            return await airflow.pause_dag(arguments["dag_id"])
        elif name == "unpause_dag":
            if "dag_id" not in arguments:
                raise ValueError("Missing required argument 'dag_id'")
            return await airflow.unpause_dag(arguments["dag_id"])
        elif name == "trigger_dag":
            if "dag_id" not in arguments:
                raise ValueError("Missing required argument 'dag_id'")
            return await airflow.trigger_dag(arguments["dag_id"])
        elif name == "get_dag_runs":
            if "dag_id" not in arguments:
                raise ValueError("Missing required argument 'dag_id'")
            return await airflow.get_dag_runs(
                dag_id=arguments["dag_id"],
                limit=arguments.get("limit"),
                offset=arguments.get("offset"),
                execution_date_gte=arguments.get("execution_date_gte"),
                execution_date_lte=arguments.get("execution_date_lte"),
                start_date_gte=arguments.get("start_date_gte"),
                start_date_lte=arguments.get("start_date_lte"),
                end_date_gte=arguments.get("end_date_gte"),
                end_date_lte=arguments.get("end_date_lte"),
                updated_at_gte=arguments.get("updated_at_gte"),
                updated_at_lte=arguments.get("updated_at_lte"),
                state=arguments.get("state"),
                order_by=arguments.get("order_by"),
            )
        elif name == "get_dag_tasks":
            if "dag_id" not in arguments:
                raise ValueError("Missing required argument 'dag_id'")
            return await airflow.get_dag_tasks(arguments["dag_id"])
        elif name == "get_task_instance":
            if "dag_id" not in arguments or "task_id" not in arguments or "dag_run_id" not in arguments:
                raise ValueError("Missing required arguments 'dag_id', 'task_id', or 'dag_run_id'")
            return await airflow.get_task_instance(arguments["dag_id"], arguments["task_id"], arguments["dag_run_id"])
        elif name == "list_task_instances":
            if "dag_id" not in arguments or "dag_run_id" not in arguments:
                raise ValueError("Missing required arguments 'dag_id' or 'dag_run_id'")
            return await airflow.list_task_instances(
                dag_id=arguments["dag_id"],
                dag_run_id=arguments["dag_run_id"],
                execution_date_gte=arguments.get("execution_date_gte"),
                execution_date_lte=arguments.get("execution_date_lte"),
                start_date_gte=arguments.get("start_date_gte"),
                start_date_lte=arguments.get("start_date_lte"),
                end_date_gte=arguments.get("end_date_gte"),
                end_date_lte=arguments.get("end_date_lte"),
                updated_at_gte=arguments.get("updated_at_gte"),
                updated_at_lte=arguments.get("updated_at_lte"),
                duration_gte=arguments.get("duration_gte"),
                duration_lte=arguments.get("duration_lte"),
                state=arguments.get("state"),
                pool=arguments.get("pool"),
                queue=arguments.get("queue"),
                limit=arguments.get("limit"),
                offset=arguments.get("offset"),
            )
        elif name == "get_import_error":
            if "import_error_id" not in arguments:
                raise ValueError("Missing required argument 'import_error_id'")
            return await airflow.get_import_error(int(arguments["import_error_id"]))
        elif name == "list_import_errors":
            return await airflow.list_import_errors(
                limit=arguments.get("limit"),
                offset=arguments.get("offset"),
                order_by=arguments.get("order_by"),
            )
        elif name == "get_health":
            return await airflow.get_health()
        elif name == "get_version":
            return await airflow.get_version()

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="list_dags",
                description="Lists all DAGs in the Airflow instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "The numbers of items to return (default: 100)",
                            "minimum": 1
                        },
                        "offset": {
                            "type": "integer",
                            "description": "The number of items to skip before starting to collect the result set",
                            "minimum": 0
                        },
                        "order_by": {
                            "type": "string",
                            "description": "The name of the field to order the results by. Prefix with - to reverse sort order"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of tags to filter results"
                        },
                        "only_active": {
                            "type": "boolean",
                            "description": "Only filter active DAGs (default: true)"
                        },
                        "paused": {
                            "type": "boolean",
                            "description": "Only filter paused/unpaused DAGs. If absent, returns both"
                        },
                        "dag_id_pattern": {
                            "type": "string",
                            "description": "If set, only return DAGs with dag_ids matching this pattern"
                        }
                    }
                },
            ),
            types.Tool(
                name="get_dag",
                description="Get details of a specific DAG",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG to retrieve",
                        }
                    },
                },
            ),
            types.Tool(
                name="pause_dag",
                description="Pause a DAG",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG to pause",
                        }
                    },
                },
            ),
            types.Tool(
                name="unpause_dag",
                description="Unpause a DAG",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG to unpause",
                        }
                    },
                },
            ),
            types.Tool(
                name="trigger_dag",
                description="Trigger a DAG run",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG to trigger",
                        }
                    },
                },
            ),
            types.Tool(
                name="get_dag_runs",
                description="Get DAG runs for a specific DAG",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG to retrieve DAG runs for",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "The numbers of items to return (default: 100)",
                            "minimum": 1
                        },
                        "offset": {
                            "type": "integer",
                            "description": "The number of items to skip before starting to collect the result set",
                            "minimum": 0
                        },
                        "execution_date_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal to the specified date"
                        },
                        "execution_date_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less than or equal to the specified date"
                        },
                        "start_date_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal the specified date"
                        },
                        "start_date_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less or equal the specified date"
                        },
                        "end_date_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal the specified date"
                        },
                        "end_date_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less than or equal to the specified date"
                        },
                        "updated_at_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal the specified date"
                        },
                        "updated_at_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less or equal the specified date"
                        },
                        "state": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The value can be repeated to retrieve multiple matching values (OR condition)"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "The name of the field to order the results by. Prefix with - to reverse sort order"
                        }
                    }
                },
            ),
            types.Tool(
                name="get_dag_tasks",
                description="Get tasks for a specific DAG",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG to retrieve tasks for",
                        }
                    },
                },
            ),
            types.Tool(
                name="get_task_instance",
                description="Get details of a specific task instance",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id", "task_id", "dag_run_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG",
                        },
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the task",
                        },
                        "dag_run_id": {
                            "type": "string",
                            "description": "The ID of the DAG run",
                        }
                    },
                },
            ),
            types.Tool(
                name="list_task_instances",
                description="List all task instances for a specific DAG run",
                inputSchema={
                    "type": "object",
                    "required": ["dag_id", "dag_run_id"],
                    "properties": {
                        "dag_id": {
                            "type": "string",
                            "description": "The ID of the DAG",
                        },
                        "dag_run_id": {
                            "type": "string",
                            "description": "The ID of the DAG run",
                        },
                        "execution_date_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal to the specified date"
                        },
                        "execution_date_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less than or equal to the specified date"
                        },
                        "start_date_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal the specified date"
                        },
                        "start_date_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less or equal the specified date"
                        },
                        "end_date_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal the specified date"
                        },
                        "end_date_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less than or equal to the specified date"
                        },
                        "updated_at_gte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects greater or equal the specified date"
                        },
                        "updated_at_lte": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Returns objects less or equal the specified date"
                        },
                        "duration_gte": {
                            "type": "number",
                            "description": "Returns objects greater than or equal to the specified values"
                        },
                        "duration_lte": {
                            "type": "number",
                            "description": "Returns objects less than or equal to the specified values"
                        },
                        "state": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "States of the task instance. The value can be repeated to retrieve multiple matching values (OR condition)"
                        },
                        "pool": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The value can be repeated to retrieve multiple matching values (OR condition)"
                        },
                        "queue": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The value can be repeated to retrieve multiple matching values (OR condition)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "The numbers of items to return (default: 100)",
                            "minimum": 1
                        },
                        "offset": {
                            "type": "integer",
                            "description": "The number of items to skip before starting to collect the result set",
                            "minimum": 0
                        }
                    }
                },
            ),
            types.Tool(
                name="get_import_error",
                description="Get details of a specific import error",
                inputSchema={
                    "type": "object",
                    "required": ["import_error_id"],
                    "properties": {
                        "import_error_id": {
                            "type": "integer",
                            "description": "The ID of the import error to retrieve",
                        }
                    },
                },
            ),
            types.Tool(
                name="list_import_errors",
                description="List all import errors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "The numbers of items to return (default: 100)",
                            "minimum": 1
                        },
                        "offset": {
                            "type": "integer",
                            "description": "The number of items to skip before starting to collect the result set",
                            "minimum": 0
                        },
                        "order_by": {
                            "type": "string",
                            "description": "The name of the field to order the results by. Prefix with - to reverse sort order"
                        }
                    }
                },
            ),
            types.Tool(
                name="get_health",
                description="Get the health status of the Airflow instance",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
            ),
            types.Tool(
                name="get_version",
                description="Get the version information of the Airflow instance",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
            ),
        ]

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0