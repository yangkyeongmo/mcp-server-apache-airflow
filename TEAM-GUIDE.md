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

## Real Example: Analyzing Manual DAG Run Configurations

This actual conversation shows how the AI uses the MCP tools to investigate DAG runs, handle partial information, and extract insights.

**User prompt:** *"Get the manual DAG runs configuration details for the stage0_prep DAG"*

**AI response:**

> I'll help you retrieve the manual DAG runs configuration details for the "stage0_prep" DAG. Let me query the Airflow server for this information.

The AI first tries to get DAG runs:

```
🔧 get_dag_runs
   dag_id: "stage0_prep"
   order_by: "-execution_date"
   limit: 100

→ Result: No DAG runs found
```

The query returned no results, so the AI searches for matching DAGs:

```
🔧 fetch_dags
   dag_id_pattern: "stage0"
   limit: 50

→ Found: "arc_final_proposal_ingest_stage0_prep"
```

Now with the correct DAG ID, it retrieves the runs:

```
🔧 get_dag_runs
   dag_id: "arc_final_proposal_ingest_stage0_prep"
   limit: 100
   order_by: "-execution_date"

→ Result: 120 manual runs found
```

**Final AI Summary:**

### Manual DAG Run Configuration Summary for `arc_final_proposal_ingest_stage0_prep`

**Total Manual Runs**: 120

#### States Processed:
| State | Runs |
|-------|------|
| VA (Virginia) | 21 |
| AZ (Arizona) | 12 |
| XY (Test) | 9 |
| LA (Louisiana) | 7 |
| AR (Arkansas) | 6 |
| OK (Oklahoma) | 5 |
| GU (Guam) | 3 |
| TX (Texas) | 3 |
| MN (Minnesota) | 2 |
| MS (Mississippi) | 1 |

#### Common Config Patterns:

**clean_up_transformed_table**: `True` (~62%) / `False` (~38%)

**dp_rp_relationship_type**:
- `"1DP-1RP"` (One-to-One)
- `"provided-deployment_reporting.csv"` (CSV file)

**sa_agreement_type**:
- `"1Provider-1SA"` (One Provider, One Subgrant)
- `"provided-subgrant_agreements.csv"` (CSV file)

#### Example Configurations:

```json
// Arizona
{
  "clean_up_transformed_table": true,
  "state": "AZ",
  "version_date": "2026-01-05",
  "gdrive_folder_id": "1TUnYWUlIiABZ4wFF0ms6gcuIHJgXN-RI",
  "sa_agreement_type": "1Provider-1SA",
  "dp_rp_relationship_type": "provided-deployment_reporting.csv"
}

// Virginia
{
  "clean_up_transformed_table": true,
  "state": "VA",
  "version_date": "2025-12-15",
  "gdrive_folder_id": "1LUGh4IEQpO2X9AfoauwlfM2ldzB1GdRJ"
}
```

**Run Status**: 118 successful, 2 failed
**Date Range**: 2025-11-27 to 2026-01-28
**Typical Duration**: 6-8 minutes per run

---

**Key Takeaway**: The AI handled the partial DAG name gracefully, searched for matches, found the correct DAG, and summarized 120 runs into actionable insights — all from a single prompt.

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
