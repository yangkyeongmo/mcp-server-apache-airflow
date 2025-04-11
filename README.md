# mcp-server-apache-airflow

[![smithery badge](https://smithery.ai/badge/@yangkyeongmo/mcp-server-apache-airflow)](https://smithery.ai/server/@yangkyeongmo/mcp-server-apache-airflow)

A Model Context Protocol (MCP) server implementation for Apache Airflow, enabling seamless integration with MCP clients. This project provides a standardized way to interact with Apache Airflow through the Model Context Protocol.

<a href="https://glama.ai/mcp/servers/e99b6vx9lw">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/e99b6vx9lw/badge" alt="Server for Apache Airflow MCP server" />
</a>

## About

This project implements a [Model Context Protocol](https://modelcontextprotocol.io/introduction) server that wraps Apache Airflow's REST API, allowing MCP clients to interact with Airflow in a standardized way. It uses the official Apache Airflow client library to ensure compatibility and maintainability.

## Feature Implementation Status

| Feature                          | API Path                                                                                      | Status |
| -------------------------------- | --------------------------------------------------------------------------------------------- | ------ |
| **DAG Management**         |                                                                                               |        |
| List DAGs                        | `/api/v1/dags`                                                                              | ✅     |
| Get DAG Details                  | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Pause DAG                        | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Unpause DAG                      | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Update DAG                       | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Delete DAG                       | `/api/v1/dags/{dag_id}`                                                                     | ✅     |
| Get DAG Source                   | `/api/v1/dagSources/{file_token}`                                                           | ✅     |
| Patch Multiple DAGs              | `/api/v1/dags`                                                                              | ✅     |
| Reparse DAG File                 | `/api/v1/dagSources/{file_token}/reparse`                                                   | ✅     |
| **DAG Runs**               |                                                                                               |        |
| List DAG Runs                    | `/api/v1/dags/{dag_id}/dagRuns`                                                             | ✅     |
| Create DAG Run                   | `/api/v1/dags/{dag_id}/dagRuns`                                                             | ✅     |
| Get DAG Run Details              | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}`                                                | ✅     |
| Update DAG Run                   | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}`                                                | ✅     |
| Delete DAG Run                   | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}`                                                | ✅     |
| Get DAG Runs Batch               | `/api/v1/dags/~/dagRuns/list`                                                               | ✅     |
| Clear DAG Run                    | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/clear`                                          | ✅     |
| Set DAG Run Note                 | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/setNote`                                        | ✅     |
| Get Upstream Dataset Events      | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/upstreamDatasetEvents`                          | ✅     |
| **Tasks**                  |                                                                                               |        |
| List DAG Tasks                   | `/api/v1/dags/{dag_id}/tasks`                                                               | ✅     |
| Get Task Details                 | `/api/v1/dags/{dag_id}/tasks/{task_id}`                                                     | ✅     |
| Get Task Instance                | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}`                        | ✅     |
| List Task Instances              | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances`                                  | ✅     |
| Update Task Instance             | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}`                        | ✅     |
| Clear Task Instances             | `/api/v1/dags/{dag_id}/clearTaskInstances`                                                  | ✅     |
| Set Task Instances State         | `/api/v1/dags/{dag_id}/updateTaskInstancesState`                                            | ✅     |
| **Variables**              |                                                                                               |        |
| List Variables                   | `/api/v1/variables`                                                                         | ✅     |
| Create Variable                  | `/api/v1/variables`                                                                         | ✅     |
| Get Variable                     | `/api/v1/variables/{variable_key}`                                                          | ✅     |
| Update Variable                  | `/api/v1/variables/{variable_key}`                                                          | ✅     |
| Delete Variable                  | `/api/v1/variables/{variable_key}`                                                          | ✅     |
| **Connections**            |                                                                                               |        |
| List Connections                 | `/api/v1/connections`                                                                       | ✅     |
| Create Connection                | `/api/v1/connections`                                                                       | ✅     |
| Get Connection                   | `/api/v1/connections/{connection_id}`                                                       | ✅     |
| Update Connection                | `/api/v1/connections/{connection_id}`                                                       | ✅     |
| Delete Connection                | `/api/v1/connections/{connection_id}`                                                       | ✅     |
| Test Connection                  | `/api/v1/connections/test`                                                                  | ✅     |
| **Pools**                  |                                                                                               |        |
| List Pools                       | `/api/v1/pools`                                                                             | ✅     |
| Create Pool                      | `/api/v1/pools`                                                                             | ✅     |
| Get Pool                         | `/api/v1/pools/{pool_name}`                                                                 | ✅     |
| Update Pool                      | `/api/v1/pools/{pool_name}`                                                                 | ✅     |
| Delete Pool                      | `/api/v1/pools/{pool_name}`                                                                 | ✅     |
| **XComs**                  |                                                                                               |        |
| List XComs                       | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries`            | ✅     |
| Get XCom Entry                   | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries/{xcom_key}` | ✅     |
| **Datasets**               |                                                                                               |        |
| List Datasets                    | `/api/v1/datasets`                                                                          | ✅     |
| Get Dataset                      | `/api/v1/datasets/{uri}`                                                                    | ✅     |
| Get Dataset Events               | `/api/v1/datasetEvents`                                                                     | ✅     |
| Create Dataset Event             | `/api/v1/datasetEvents`                                                                     | ✅     |
| Get DAG Dataset Queued Event     | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents/{uri}`                                  | ✅     |
| Get DAG Dataset Queued Events    | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents`                                        | ✅     |
| Delete DAG Dataset Queued Event  | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents/{uri}`                                  | ✅     |
| Delete DAG Dataset Queued Events | `/api/v1/dags/{dag_id}/dagRuns/queued/datasetEvents`                                        | ✅     |
| Get Dataset Queued Events        | `/api/v1/datasets/{uri}/dagRuns/queued/datasetEvents`                                       | ✅     |
| Delete Dataset Queued Events     | `/api/v1/datasets/{uri}/dagRuns/queued/datasetEvents`                                       | ✅     |
| **Monitoring**             |                                                                                               |        |
| Get Health                       | `/api/v1/health`                                                                            | ✅     |
| **DAG Stats**              |                                                                                               |        |
| Get DAG Stats                    | `/api/v1/dags/statistics`                                                                   | ✅     |
| **Config**                 |                                                                                               |        |
| Get Config                       | `/api/v1/config`                                                                            | ✅     |
| **Plugins**                |                                                                                               |        |
| Get Plugins                      | `/api/v1/plugins`                                                                           | ✅     |
| **Providers**              |                                                                                               |        |
| List Providers                   | `/api/v1/providers`                                                                         | ✅     |
| **Event Logs**             |                                                                                               |        |
| List Event Logs                  | `/api/v1/eventLogs`                                                                         | ✅     |
| Get Event Log                    | `/api/v1/eventLogs/{event_log_id}`                                                          | ✅     |
| **System**                 |                                                                                               |        |
| Get Import Errors                | `/api/v1/importErrors`                                                                      | ✅     |
| Get Import Error Details         | `/api/v1/importErrors/{import_error_id}`                                                    | ✅     |
| Get Health Status                | `/api/v1/health`                                                                            | ✅     |
| Get Version                      | `/api/v1/version`                                                                           | ✅     |

## Setup

### Dependencies

This project depends on the official Apache Airflow client library (`apache-airflow-client`). It will be automatically installed when you install this package.

### Environment Variables

Set the following environment variables:

```
AIRFLOW_HOST=<your-airflow-host>
AIRFLOW_USERNAME=<your-airflow-username>
AIRFLOW_PASSWORD=<your-airflow-password>
AIRFLOW_API_VERSION=v1  # Optional, defaults to v1
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

### Selecting the API groups

You can select the API groups you want to use by setting the `--apis` flag.

```bash
uv run mcp-server-apache-airflow --apis "dag,dagrun"
```

The default is to use all APIs.

Allowed values are:

- config
- connections
- dag
- dagrun
- dagstats
- dataset
- eventlog
- importerror
- monitoring
- plugin
- pool
- provider
- taskinstance
- variable
- xcom

### Manual Execution

You can also run the server manually:

```bash
make run
```

`make run` accepts following options:

Options:

- `--port`: Port to listen on for SSE (default: 8000)
- `--transport`: Transport type (stdio/sse, default: stdio)

Or, you could run the sse server directly, which accepts same parameters:

```bash
make run-sse
```

### Installing via Smithery

To install Apache Airflow MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@yangkyeongmo/mcp-server-apache-airflow):

```bash
npx -y @smithery/cli install @yangkyeongmo/mcp-server-apache-airflow --client claude
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
