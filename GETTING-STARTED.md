# Getting Started: Airflow MCP Server

Quick setup and example prompts for using the Airflow MCP with AI coding assistants.

---

## Setup (5 minutes)

### 1. Install

```bash
git clone https://github.com/zedahmed144/mcp-server-apache-airflow
cd mcp-server-apache-airflow
uv sync --extra sso
uv run playwright install chromium
```

### 2. Configure Claude Code

```bash
./setup-mcp.sh claude
```

Restart Claude Code → SSO login opens → Test: *"List all Airflow DAGs"*

### 3. Configure AmpCode

```bash
./setup-mcp.sh rest
```

**Important:** AmpCode MIGHT also requires manual setup in the UI:
1. Open AmpCode → MCP Servers panel → **+ Add**
2. Fill in:
   - **Server Name:** `airflow-sso`
   - **Command:** `uv`
   - **Arguments:** `run --directory /path/to/mcp-server-apache-airflow --extra sso mcp-server-apache-airflow`
3. Add environment variables:
   - `AIRFLOW_HOST` = `https://pidgey.ready-internal.net`
   - `AIRFLOW_SSO_AUTH` = `true`
   - `AIRFLOW_STATE_DIR` = `/path/to/mcp-server-apache-airflow/.airflow_state`
   - `READ_ONLY` = `true`

### 4. Configure VSCode Copilot

The `./setup-mcp.sh rest` command creates `.vscode/mcp.json`. Just restart VSCode.

### 5. Disable When Not Needed

```bash
./setup-mcp.sh disable   # No login prompts when off VPN
./setup-mcp.sh enable    # Re-enable when needed
```

---

## Example Prompts

| Prompt                                               | What it does          |
| ---------------------------------------------------- | --------------------- |
| *"List all Airflow DAGs"*                            | Shows available DAGs  |
| *"Are there any failed DAG runs today?"*             | Checks for failures   |
| *"Why did `my_dag` fail yesterday? Show error logs"* | Investigates failures |

---

## Real Examples

See [examples/](examples/) for detailed MCP interactions:

| Example                                                        | Description                                   |
| -------------------------------------------------------------- | --------------------------------------------- |
| [Analyze DAG Run Configs](examples/analyze-dag-run-configs.md) | Extract config patterns from 120+ manual runs |

---

## Links

- [README](README.md) - Full documentation, troubleshooting, architecture
- [setup-mcp.sh](setup-mcp.sh) - Setup and toggle MCP configs
- [update-hosts.sh](update-hosts.sh) - VPN DNS fix
