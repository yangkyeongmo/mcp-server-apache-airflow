[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/yangkyeongmo-mcp-server-apache-airflow-badge.png)](https://mseep.ai/app/yangkyeongmo-mcp-server-apache-airflow)

# mcp-server-apache-airflow

[![smithery badge](https://smithery.ai/badge/@yangkyeongmo/mcp-server-apache-airflow)](https://smithery.ai/server/@yangkyeongmo/mcp-server-apache-airflow)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-server-apache-airflow)

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
| Get Task Instance Log            | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{task_try_number}` | ✅     |
| Clear Task Instances             | `/api/v1/dags/{dag_id}/clearTaskInstances`                                                  | ✅     |
| Set Task Instances State         | `/api/v1/dags/{dag_id}/updateTaskInstancesState`                                            | ✅     |
| List Task Instance Tries         | `/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/tries`                  | ✅     |
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
AIRFLOW_HOST=<your-airflow-host>        # Optional, defaults to http://localhost:8080
AIRFLOW_API_VERSION=v1                  # Optional, defaults to v1
READ_ONLY=true                          # Optional, enables read-only mode (true/false, defaults to false)
```

#### Authentication

Choose one of the following authentication methods:

**Basic Authentication (default):**
```
AIRFLOW_USERNAME=<your-airflow-username>
AIRFLOW_PASSWORD=<your-airflow-password>
```

**JWT Token Authentication:**
```
AIRFLOW_JWT_TOKEN=<your-jwt-token>
```

To obtain a JWT token, you can use Airflow's authentication endpoint:

```bash
ENDPOINT_URL="http://localhost:8080"  # Replace with your Airflow endpoint
curl -X 'POST' \
  "${ENDPOINT_URL}/auth/token" \
  -H 'Content-Type: application/json' \
  -d '{ "username": "<your-username>", "password": "<your-password>" }'
```

> **Note**: If both JWT token and basic authentication credentials are provided, JWT token takes precedence.

**JWT Token with Automatic Refresh:**

For environments where JWT tokens expire (e.g., Cloud Composer, managed Airflow services), you can configure automatic token refresh:

```
AIRFLOW_JWT_TOKEN=<your-jwt-token>                              # Optional: initial token
AIRFLOW_JWT_TOKEN_REFRESH_COMMAND=<command-to-refresh-token>    # Required: command to obtain new token
```

The server supports two modes:

1. **With initial token**: If `AIRFLOW_JWT_TOKEN` is provided, the server uses it immediately and only executes the refresh command when a 401 Unauthorized error is detected (token expired).

2. **Without initial token**: If only `AIRFLOW_JWT_TOKEN_REFRESH_COMMAND` is provided, the server executes the command on initialization to obtain the initial token.

**Examples for different environments:**

*Google Cloud Composer:*
```
AIRFLOW_JWT_TOKEN_REFRESH_COMMAND=gcloud auth print-access-token
```

*AWS MWAA (using aws-cli):*
```
AIRFLOW_JWT_TOKEN_REFRESH_COMMAND=aws mwaa create-web-login-token --name your-environment-name --region your-region --query WebToken --output text
```

*Azure Managed Airflow:*
```
AIRFLOW_JWT_TOKEN_REFRESH_COMMAND=az account get-access-token --resource https://airflow.azure.com --query accessToken --output tsv
```

*Custom command (any shell command that outputs a token):*
```
AIRFLOW_JWT_TOKEN_REFRESH_COMMAND=/path/to/your/script.sh
```

Internally, the server uses a small authentication layer to configure the official Apache Airflow client:

- A `Configuration` object is created using `AIRFLOW_HOST` and `AIRFLOW_API_VERSION`.
- Authentication is applied with the following precedence:
  1. Static JWT token via `AIRFLOW_JWT_TOKEN`
  2. JWT token obtained via `AIRFLOW_JWT_TOKEN_REFRESH_COMMAND`
  3. Basic auth via `AIRFLOW_USERNAME` and `AIRFLOW_PASSWORD`
- A factory function `create_airflow_api_client()` builds the `ApiClient` instance and, when configured, wraps it with automatic JWT refresh support.

Most users do not need to interact with this layer directly, but it is useful context if you are extending the server or running it as a library.

### Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

**Basic Authentication:**
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

**JWT Token Authentication:**
```json
{
  "mcpServers": {
    "mcp-server-apache-airflow": {
      "command": "uvx",
      "args": ["mcp-server-apache-airflow"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_JWT_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

**JWT Token with Automatic Refresh (e.g., Google Cloud Composer):**
```json
{
  "mcpServers": {
    "mcp-server-apache-airflow": {
      "command": "uvx",
      "args": ["mcp-server-apache-airflow"],
      "env": {
        "AIRFLOW_HOST": "https://your-composer-airflow-url",
        "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "gcloud auth print-access-token"
      }
    }
  }
}
```

For read-only mode (recommended for safety):

**Basic Authentication:**
```json
{
  "mcpServers": {
    "mcp-server-apache-airflow": {
      "command": "uvx",
      "args": ["mcp-server-apache-airflow"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_USERNAME": "your-username",
        "AIRFLOW_PASSWORD": "your-password",
        "READ_ONLY": "true"
      }
    }
  }
}
```

**JWT Token Authentication:**
```json
{
  "mcpServers": {
    "mcp-server-apache-airflow": {
      "command": "uvx",
      "args": ["mcp-server-apache-airflow", "--read-only"],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-host",
        "AIRFLOW_JWT_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

Alternative configuration using `uv`:

**Basic Authentication:**
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

**JWT Token Authentication:**
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
        "AIRFLOW_JWT_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

**JWT Token with Automatic Refresh (e.g., Google Cloud Composer):**
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
        "AIRFLOW_HOST": "https://your-composer-airflow-url",
        "AIRFLOW_JWT_TOKEN_REFRESH_COMMAND": "gcloud auth print-access-token"
      }
    }
  }
}
```

Replace `/path/to/mcp-server-apache-airflow` with the actual path where you've cloned the repository.

### Selecting the API groups

You can select the API groups you want to use by setting the `--apis` flag.

```bash
uv run mcp-server-apache-airflow --apis dag --apis dagrun
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

### Read-Only Mode

You can run the server in read-only mode by using the `--read-only` flag or by setting the `READ_ONLY=true` environment variable. This will only expose tools that perform read operations (GET requests) and exclude any tools that create, update, or delete resources.

Using the command-line flag:
```bash
uv run mcp-server-apache-airflow --read-only
```

Using the environment variable:
```bash
READ_ONLY=true uv run mcp-server-apache-airflow
```

In read-only mode, the server will only expose tools like:
- Listing DAGs, DAG runs, tasks, variables, connections, etc.
- Getting details of specific resources
- Reading configurations and monitoring information
- Testing connections (non-destructive)

Write operations like creating, updating, deleting DAGs, variables, connections, triggering DAG runs, etc. will not be available in read-only mode.

You can combine read-only mode with API group selection:

```bash
uv run mcp-server-apache-airflow --read-only --apis dag --apis variable
```

### Manual Execution

You can also run the server manually:

```bash
make run
```

`make run` accepts following options:

Options:

- `--port`: Port to listen on for SSE (default: 8000)
- `--transport`: Transport type (stdio/sse/http, default: stdio)

Or, you could run the sse server directly, which accepts same parameters:

```bash
make run-sse
```

Also, you could start service directly using `uv` like in the following command:

```bash
uv run src --transport http --port 8080
```

### Installing via Smithery

To install Apache Airflow MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@yangkyeongmo/mcp-server-apache-airflow):

```bash
npx -y @smithery/cli install @yangkyeongmo/mcp-server-apache-airflow --client claude
```

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yangkyeongmo/mcp-server-apache-airflow.git
cd mcp-server-apache-airflow
```

2. Install development dependencies:
```bash
uv sync --dev
```

3. Create a `.env` file for environment variables (optional for development):
```bash
touch .env
```

> **Note**: No environment variables are required for running tests. The `AIRFLOW_HOST` defaults to `http://localhost:8080` for development and testing purposes.

### Running Tests

The project uses pytest for testing with the following commands available:

```bash
# Run all tests
make test
```

### Code Quality

```bash
# Run linting
make lint

# Run code formatting
make format
```

### Continuous Integration

The project includes a GitHub Actions workflow (`.github/workflows/test.yml`) that automatically:

- Runs tests on Python 3.10, 3.11, and 3.12
- Executes linting checks using ruff
- Runs on every push and pull request to `main` branch

The CI pipeline ensures code quality and compatibility across supported Python versions before any changes are merged.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

The package is deployed automatically to PyPI when project.version is updated in `pyproject.toml`.
Follow semver for versioning.

Please include version update in the PR in order to apply the changes to core logic.

## License

[MIT License](LICENSE)
