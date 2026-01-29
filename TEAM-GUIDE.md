# Team Guide: Airflow MCP Server

Quick start guide and practical examples for using the Airflow MCP server with AI coding assistants.

---

## Quick Start (5 minutes)

### Prerequisites

- VPN connected to internal network
- [uv](https://github.com/astral-sh/uv) installed (`brew install uv`)
- Claude Code, AmpCode, or VSCode with GitHub Copilot

### Setup

```bash
# Clone and install
git clone https://github.com/zedahmed144/mcp-server-apache-airflow
cd mcp-server-apache-airflow
uv sync --extra sso
uv run playwright install chromium

# Setup Claude Code first (triggers SSO login)
./setup-mcp.sh claude
```

Then:
1. **Restart Claude Code** in this project folder
2. Browser opens → complete SSO login
3. Test: *"List all Airflow DAGs"*

Once working, setup other tools:
```bash
./setup-mcp.sh rest   # AmpCode + VSCode
```

---

## Real Examples

See the [examples/](examples/) folder for real-world MCP interactions:

| Example | Description |
|---------|-------------|
| [Analyze DAG Run Configs](examples/analyze-dag-run-configs.md) | Extract configuration patterns from 120+ manual DAG runs |

*Add your own examples as you discover useful patterns!*

---

## Example Prompts

### Exploring DAGs

| Prompt | What it does |
|--------|--------------|
| *"List all Airflow DAGs"* | Shows all available DAGs |
| *"Show me the DAG named `etl_pipeline`"* | Gets details for a specific DAG |
| *"What DAGs are currently paused?"* | Lists paused DAGs |
| *"Show DAGs tagged with `production`"* | Filters by tag |

### Monitoring Runs

| Prompt | What it does |
|--------|--------------|
| *"Show recent DAG runs for `daily_report`"* | Lists run history |
| *"Are there any failed DAG runs today?"* | Checks for failures |
| *"What's the status of the last `etl_pipeline` run?"* | Gets latest run status |
| *"Show me all running DAGs"* | Lists currently executing DAGs |

### Task Details

| Prompt | What it does |
|--------|--------------|
| *"List all tasks in the `etl_pipeline` DAG"* | Shows task structure |
| *"Show logs for the `extract` task in today's run"* | Fetches task logs |
| *"Which tasks failed in the last `daily_report` run?"* | Identifies failed tasks |
| *"What's the duration of each task in `etl_pipeline`?"* | Performance analysis |

### Debugging

| Prompt | What it does |
|--------|--------------|
| *"Why did `daily_report` fail yesterday?"* | Investigates failure cause |
| *"Show me the error logs for failed task `transform`"* | Gets error details |
| *"Compare the last successful vs failed run of `etl_pipeline`"* | Diff analysis |
| *"What changed between these two DAG runs?"* | Timeline comparison |

### Administrative

| Prompt | What it does |
|--------|--------------|
| *"Show Airflow health status"* | Checks instance health |
| *"List all Airflow connections"* | Shows configured connections |
| *"What variables are set in Airflow?"* | Lists Airflow variables |
| *"Show the import errors"* | Checks for DAG import issues |

---

## Optimal Usage Patterns

### 1. Morning Check-in

Start your day with a quick health check:

> *"Give me a summary of overnight DAG runs - any failures or issues I should know about?"*

### 2. Investigating Alerts

When you get a PagerDuty/Slack alert:

> *"The `customer_sync` DAG failed at 3am. Show me the error logs and what task failed."*

### 3. Pre-deployment Review

Before deploying DAG changes:

> *"Show me the recent run history for `etl_pipeline` - success rate and average duration over the last week."*

### 4. Capacity Planning

Understanding resource usage:

> *"Which DAGs are taking the longest to run? Show me the top 5 by average duration."*

### 5. Dependency Analysis

Understanding DAG relationships:

> *"What datasets does `daily_report` depend on? Show me the upstream DAGs."*

---

## Tips & Best Practices

### Be Specific
Instead of: *"Show DAG info"*
Use: *"Show me the `etl_pipeline` DAG including its schedule and last 5 runs"*

### Ask Follow-ups
The AI remembers context within a conversation:
1. *"List failed DAG runs from today"*
2. *"Show me the logs for the first one"*
3. *"What was different about yesterday's successful run?"*

### Combine with Code Context
When in a DAG file:
> *"This DAG keeps failing on the `transform` task. Show me the recent logs and suggest what might be wrong."*

### Use for Documentation
> *"Generate a markdown summary of the `etl_pipeline` DAG - its purpose, schedule, tasks, and dependencies."*

---

## Troubleshooting

### MCP Not Connecting

```bash
# Check status
./setup-mcp.sh status

# Verify VPN DNS
nslookup pidgey.ready-internal.net

# If DNS fails, run hosts fix
sudo ./update-hosts.sh
```

### SSO Session Expired

```bash
# Delete cookies to force re-login
rm -rf .airflow_state/cookies.enc
# Restart your AI tool
```

### Wrong Airflow Instance

Edit your personal config (`.mcp.json`, `.amp/settings.json`, or `.vscode/mcp.json`) and update `AIRFLOW_HOST`.

---

## Read-Only Mode

By default, the MCP server runs in **read-only mode** (`READ_ONLY=true`). This means:

- ✅ View DAGs, runs, tasks, logs
- ✅ List connections, variables, pools
- ✅ Check health and status
- ❌ Cannot trigger DAG runs
- ❌ Cannot pause/unpause DAGs
- ❌ Cannot modify variables or connections

To enable write operations, set `READ_ONLY=false` in your config (use with caution).

---

## Links

- [Main README](README.md) - Full documentation
- [Setup Script](setup-mcp.sh) - MCP config setup
- [VPN DNS Fix](update-hosts.sh) - For DNS resolution issues
