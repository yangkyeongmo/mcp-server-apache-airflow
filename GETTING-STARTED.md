# Getting Started: Airflow MCP Server

Quick setup and example prompts for using the Airflow MCP with AI coding assistants.

---

## Setup

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

### 3. Configure VSCode Copilot

```bash
./setup-mcp.sh vscode
```

Restart VSCode → uses saved SSO cookies.

### 4. Configure AmpCode

```bash
./setup-mcp.sh ampcode
```

Restart VSCode/AmpCode → uses saved SSO cookies.

> **Note:** Amp VSCode Extension reads from global VSCode settings, not project files.
> The script adds `airflow-sso` to `~/Library/Application Support/Code/User/settings.json`.
> Unlike Claude Code/VSCode, AmpCode ignores `"disabled": true` — so we must fully remove
> the config when disabling (and re-add when enabling).
> See [ampcode.com/manual](https://ampcode.com/manual#configuration) for details.

### 5. Disable When Not on VPN

```bash
./setup-mcp.sh disable   # Disables all MCP configs (no login prompts)
./setup-mcp.sh enable    # Re-enable when back on VPN
./setup-mcp.sh status    # Check current status
```

**How disable/enable works:**

| Tool | Disable | Enable |
|------|---------|--------|
| Claude Code | Renames `.mcp.json` → `.mcp.json.disabled` | Restores file |
| VSCode Copilot | Renames `.vscode/mcp.json` → `.disabled` | Restores file |
| AmpCode | Removes `airflow-sso` from VSCode settings | Re-adds config |

> **Why not `"disabled": true` for AmpCode?** We tried toggling a `"disabled"` property (like
> other MCP clients support), but AmpCode ignores it and still attempts to connect — launching
> the Chromium SSO browser even when off VPN. Full removal is required to silence it.

---

## Tips

**Daily workflow:** Once initial setup is done, just use:
```bash
./setup-mcp.sh enable    # Reconnects all 3 agents when back on VPN
./setup-mcp.sh disable   # Disconnects all when leaving VPN
```

**First-time setup shortcut:** After step 2 (Claude Code + SSO login), you can skip steps 3-4 and just run `./setup-mcp.sh enable` — it will configure all three tools at once.

**When SSO token expires:** Don't use `enable`. Instead, run `./setup-mcp.sh claude` first to trigger fresh SSO login, then `./setup-mcp.sh enable` for the rest.

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
- [Airflow MCP Servers](AIRFLOW-MCP-SERVERS.md) - Alternative servers comparison, Airflow v3 migration
- [setup-mcp.sh](setup-mcp.sh) - Setup and toggle MCP configs
- [update-hosts.sh](update-hosts.sh) - VPN DNS fix
