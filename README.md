# mcp-server-apache-airflow

A Model Context Protocol (MCP) server implementation for Apache Airflow, enabling seamless integration with MCP clients. This project provides a standardized way to interact with Apache Airflow through the Model Context Protocol.

## About

This project implements a [Model Context Protocol](https://modelcontextprotocol.io/introduction) server that wraps Apache Airflow's REST API, allowing MCP clients to interact with Airflow in a standardized way.

## Feature Implementation Status

| Feature | API Path | Status |
|---------|----------|--------|
| **DAG Management** | | |
| List DAGs | `/api/v1/dags` | ✅ |
| Get DAG Details | `/api/v1/dags/{dag_id}` | ✅ |
| Pause DAG | `/api/v1/dags/{dag_id}` | ✅ |
| Unpause DAG | `/api/v1/dags/{dag_id}` | ✅ |
| Update DAG | `/api/v1/dags/{dag_id}` | ❌ |
| Delete DAG | `/api/v1/dags/{dag_id}` | ❌ |
| **DAG Runs** | | |
| List DAG Runs | `/api/v1/dags/{dag_id}/dagRuns` | ✅ |
| Create DAG Run | `/api/v1/dags/{dag_id}/dagRuns` | ✅ |
| Get DAG Run Details | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}` | ❌ |
| Update DAG Run | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}` | ❌ |
| Delete DAG Run | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}` | ❌ |
| **Tasks** | | |
| List DAG Tasks | `/api/v1/dags/{dag_id}/tasks` | ✅ |
| Get Task Details | `/api/v1/dags/{dag_id}/tasks/{task_id}` | ❌ |
| Get Task Instance | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}` | ✅ |
| List Task Instances | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances` | ✅ |
| Update Task Instance | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}` | ❌ |
| **System** | | |
| Get Import Errors | `/api/v1/importErrors` | ✅ |
| Get Import Error Details | `/api/v1/importErrors/{import_error_id}` | ✅ |
| Get Health Status | `/api/v1/health` | ✅ |
| Get Version | `/api/v1/version` | ✅ |
| **Variables** | | |
| List Variables | `/api/v1/variables` | ❌ |
| Create Variable | `/api/v1/variables` | ❌ |
| Get Variable | `/api/v1/variables/{variable_key}` | ❌ |
| Update Variable | `/api/v1/variables/{variable_key}` | ❌ |
| Delete Variable | `/api/v1/variables/{variable_key}` | ❌ |
| **Connections** | | |
| List Connections | `/api/v1/connections` | ❌ |
| Create Connection | `/api/v1/connections` | ❌ |
| Get Connection | `/api/v1/connections/{connection_id}` | ❌ |
| Update Connection | `/api/v1/connections/{connection_id}` | ❌ |
| Delete Connection | `/api/v1/connections/{connection_id}` | ❌ |

## Setup

### Environment Variables

Set the following environment variables:
```
AIRFLOW_HOST=<your-airflow-host>
AIRFLOW_USERNAME=<your-airflow-username>
AIRFLOW_PASSWORD=<your-airflow-password>
```

### Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-server-apache-airflow": {
      "command": "uvx",
      "args": ["mcp-server-apache-airflow"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_USERNAME": "your-username",
        "AIRFLOW_PASSWORD": "your-password"
      }
    }
  }
}
```

Alternative configuration using `uv`:

```json
{
  "mcpServers": {
    "mcp-server-apache-airflow": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-server-apache-airflow",
        "run",
        "mcp-server-apache-airflow"
      ],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_USERNAME": "your-username",
        "AIRFLOW_PASSWORD": "your-password"
      }
    }
  }
}
```

Replace `/path/to/mcp-server-apache-airflow` with the actual path where you've cloned the repository.

### Manual Execution

You can also run the server manually:
```bash
python src/server.py
```

Options:
- `--port`: Port to listen on for SSE (default: 8000)
- `--transport`: Transport type (stdio/sse, default: stdio)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]


