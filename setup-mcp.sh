#!/bin/bash
#
# Airflow MCP Setup Script
# ========================
# Creates personal MCP configs from committed example templates.
# Each team member runs this script - personal configs are gitignored.
#
# SUPPORTED TOOLS:
#   - Claude Code: Project-level .mcp.json (handled by this script)
#   - VSCode Copilot: Project-level .vscode/mcp.json (handled by this script)
#   - AmpCode: Global VSCode settings (handled by this script)
#
# AMPCODE NOTE:
#   Amp VSCode Extension reads from global VSCode settings, not .amp/settings.json.
#   This script adds airflow-sso on first setup, then toggles "disabled": true/false.
#   See: https://ampcode.com/manual#configuration
#
# HOW IT WORKS:
#   - Example files (.example.json) are committed to git as templates
#   - This script copies them to active configs, replacing $PROJECT_DIR with actual path
#   - Personal configs are gitignored
#   - All tools share the same SSO cookies in .airflow_state/
#
# RECOMMENDED SETUP ORDER:
#   1. ./setup-mcp.sh claude   → Restart Claude Code → Complete SSO login
#   2. Test in Claude Code: "List all Airflow DAGs"
#   3. ./setup-mcp.sh vscode   → Restart VSCode (cookies already saved)
#   4. ./setup-mcp.sh ampcode  → Adds to VSCode settings → Restart AmpCode
#
# WHEN NOT ON VPN:
#   ./setup-mcp.sh disable     → Avoid login prompts on tool startup
#   ./setup-mcp.sh enable      → Re-enable when back on VPN
#
# Usage:
#   ./setup-mcp.sh claude   # Setup Claude Code (triggers SSO login)
#   ./setup-mcp.sh vscode   # Setup VSCode Copilot (reuses SSO cookies)
#   ./setup-mcp.sh ampcode  # Setup AmpCode (adds to VSCode settings)
#   ./setup-mcp.sh all      # Setup all three tools
#   ./setup-mcp.sh disable  # Disable all MCP configs (no login prompts)
#   ./setup-mcp.sh enable   # Re-enable all MCP configs
#   ./setup-mcp.sh status   # Show current status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# CONFIG FILE PATHS
# ============================================================================

CLAUDE_EXAMPLE="$SCRIPT_DIR/.mcp.example.json"
CLAUDE_CONFIG="$SCRIPT_DIR/.mcp.json"

VSCODE_EXAMPLE="$SCRIPT_DIR/.vscode/mcp.example.json"
VSCODE_CONFIG="$SCRIPT_DIR/.vscode/mcp.json"

# AmpCode uses global VSCode settings
AMPCODE_SETTINGS="$HOME/Library/Application Support/Code/User/settings.json"

# ============================================================================
# OUTPUT HELPERS
# ============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

show_help() {
    echo ""
    echo -e "${BLUE}Airflow MCP Setup${NC}"
    echo ""
    echo "Setup commands:"
    echo "  claude   Setup Claude Code (triggers SSO login)"
    echo "  vscode   Setup VSCode Copilot"
    echo "  ampcode  Setup AmpCode (modifies VSCode settings)"
    echo "  all      Setup all three tools"
    echo ""
    echo "Toggle commands:"
    echo "  disable  Disable all MCP configs (no login prompts when off VPN)"
    echo "  enable   Re-enable all MCP configs"
    echo "  status   Show current config status"
    echo ""
}

# ============================================================================
# AMPCODE HELPERS (VSCode Settings Manipulation)
# ============================================================================
# Uses Python to safely modify airflow-sso in VSCode settings.json.
# - ampcode_add: Adds airflow-sso config if not exists
# - ampcode_enable: Sets "disabled": false (or removes the property)
# - ampcode_disable: Sets "disabled": true
# ============================================================================

ampcode_exists() {
    if [ -f "$AMPCODE_SETTINGS" ]; then
        grep -q '"airflow-sso"' "$AMPCODE_SETTINGS" 2>/dev/null
        return $?
    fi
    return 1
}

ampcode_is_disabled() {
    if [ -f "$AMPCODE_SETTINGS" ] && ampcode_exists; then
        # Check if airflow-sso has "disabled": true
        # Use simple grep - if "disabled": true appears near "airflow-sso"
        grep -A 5 '"airflow-sso"' "$AMPCODE_SETTINGS" 2>/dev/null | grep -q '"disabled"\s*:\s*true'
        return $?
    fi
    return 1
}

ampcode_add() {
    if ! [ -f "$AMPCODE_SETTINGS" ]; then
        log_error "VSCode settings not found: $AMPCODE_SETTINGS"
        return 1
    fi

    if ampcode_exists; then
        # Already exists, just enable it
        ampcode_enable
        return $?
    fi

    # Use Python to safely add the entry
    python3 << EOF
import re
import json
import sys

settings_path = "$AMPCODE_SETTINGS"
project_dir = "$SCRIPT_DIR"

# The airflow-sso config to add
airflow_config = {
    "command": "/opt/homebrew/bin/uv",
    "args": [
        "run",
        "--directory",
        project_dir,
        "--extra",
        "sso",
        "mcp-server-apache-airflow"
    ],
    "env": {
        "AIRFLOW_HOST": "https://pidgey.ready-internal.net",
        "AIRFLOW_SSO_AUTH": "true",
        "AIRFLOW_STATE_DIR": f"{project_dir}/.airflow_state",
        "READ_ONLY": "true"
    }
}

try:
    with open(settings_path, 'r') as f:
        content = f.read()

    # Find amp.mcpServers section
    pattern = r'("amp\.mcpServers"\s*:\s*\{)'
    match = re.search(pattern, content)

    if match:
        # Insert after the opening brace
        insert_pos = match.end()
        entry_json = json.dumps(airflow_config, indent=4)
        indented = '\n'.join('        ' + line if i > 0 else line
                            for i, line in enumerate(entry_json.split('\n')))
        new_entry = f'\n        "airflow-sso": {indented},'

        new_content = content[:insert_pos] + new_entry + content[insert_pos:]

        with open(settings_path, 'w') as f:
            f.write(new_content)
        print("added")
    else:
        print("no_section")
        sys.exit(1)

except Exception as e:
    print(f"error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    result=$?
    if [ $result -eq 0 ]; then
        log_info "Added airflow-sso to AmpCode (VSCode settings)"
        return 0
    else
        log_error "Failed to add airflow-sso to VSCode settings"
        echo "  You may need to add it manually. See GETTING-STARTED.md"
        return 1
    fi
}

ampcode_disable() {
    if ! [ -f "$AMPCODE_SETTINGS" ]; then
        return 0
    fi

    if ! ampcode_exists; then
        return 0
    fi

    if ampcode_is_disabled; then
        return 0  # Already disabled
    fi

    # Use Python to set "disabled": true
    python3 << EOF
import re
import sys

settings_path = "$AMPCODE_SETTINGS"

try:
    with open(settings_path, 'r') as f:
        content = f.read()

    # Find airflow-sso block and add/update "disabled": true
    # Strategy: Find the opening of airflow-sso object and insert "disabled": true after it

    pattern = r'("airflow-sso"\s*:\s*\{)'
    match = re.search(pattern, content)

    if match:
        insert_pos = match.end()
        # Check if disabled already exists (just not true)
        disabled_pattern = r'("airflow-sso"\s*:\s*\{[^}]*)"disabled"\s*:\s*\w+'
        if re.search(disabled_pattern, content, re.DOTALL):
            # Replace existing disabled value
            content = re.sub(
                r'("airflow-sso"\s*:\s*\{[^}]*"disabled"\s*:\s*)\w+',
                r'\1true',
                content,
                flags=re.DOTALL
            )
        else:
            # Insert "disabled": true after opening brace
            new_content = content[:insert_pos] + '\n            "disabled": true,' + content[insert_pos:]
            content = new_content

        with open(settings_path, 'w') as f:
            f.write(content)
        print("disabled")
    else:
        print("not_found")

except Exception as e:
    print(f"error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    result=$?
    if [ $result -eq 0 ]; then
        log_info "Disabled airflow-sso in AmpCode"
        return 0
    fi
    return 1
}

ampcode_enable() {
    if ! [ -f "$AMPCODE_SETTINGS" ]; then
        return 1
    fi

    if ! ampcode_exists; then
        # Doesn't exist, need to add it
        ampcode_add
        return $?
    fi

    if ! ampcode_is_disabled; then
        log_warn "AmpCode airflow-sso already enabled"
        return 0  # Already enabled
    fi

    # Use Python to remove "disabled": true (or set to false)
    python3 << EOF
import re
import sys

settings_path = "$AMPCODE_SETTINGS"

try:
    with open(settings_path, 'r') as f:
        content = f.read()

    # Remove the "disabled": true line from airflow-sso block
    # Match "disabled": true with optional trailing comma and whitespace
    pattern = r'("airflow-sso"\s*:\s*\{[^}]*)\s*"disabled"\s*:\s*true,?\s*'

    new_content = re.sub(pattern, r'\1', content, flags=re.DOTALL)

    # Clean up any double commas
    new_content = re.sub(r',(\s*[,}])', r'\1', new_content)

    with open(settings_path, 'w') as f:
        f.write(new_content)
    print("enabled")

except Exception as e:
    print(f"error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    result=$?
    if [ $result -eq 0 ]; then
        log_info "Enabled airflow-sso in AmpCode"
        return 0
    fi
    return 1
}

show_status() {
    echo ""
    echo -e "${BLUE}Config Status${NC}"
    echo ""

    # Claude Code
    if [ -f "$CLAUDE_CONFIG" ]; then
        echo -e "  Claude Code  (.mcp.json)             ${GREEN}enabled${NC}"
    elif [ -f "${CLAUDE_CONFIG}.disabled" ]; then
        echo -e "  Claude Code  (.mcp.json)             ${RED}disabled${NC}"
    else
        echo -e "  Claude Code  (.mcp.json)             ${YELLOW}not setup${NC}"
    fi

    # VSCode Copilot
    if [ -f "$VSCODE_CONFIG" ]; then
        echo -e "  VSCode       (.vscode/mcp.json)      ${GREEN}enabled${NC}"
    elif [ -f "${VSCODE_CONFIG}.disabled" ]; then
        echo -e "  VSCode       (.vscode/mcp.json)      ${RED}disabled${NC}"
    else
        echo -e "  VSCode       (.vscode/mcp.json)      ${YELLOW}not setup${NC}"
    fi

    # AmpCode
    if ampcode_exists; then
        if ampcode_is_disabled; then
            echo -e "  AmpCode      (VSCode settings.json)  ${RED}disabled${NC}"
        else
            echo -e "  AmpCode      (VSCode settings.json)  ${GREEN}enabled${NC}"
        fi
    else
        echo -e "  AmpCode      (VSCode settings.json)  ${YELLOW}not setup${NC}"
    fi

    # SSO cookies
    if [ -d "$SCRIPT_DIR/.airflow_state" ]; then
        echo ""
        echo -e "  SSO cookies  (.airflow_state/)       ${GREEN}saved${NC}"
    else
        echo ""
        echo -e "  SSO cookies  (.airflow_state/)       ${YELLOW}not yet${NC}"
    fi

    echo ""
}

# ============================================================================
# CREATE CONFIG FROM EXAMPLE TEMPLATE
# ============================================================================

create_config() {
    local example="$1"
    local config="$2"
    local name="$3"

    if [ ! -f "$example" ]; then
        log_warn "Example not found: $example"
        return 1
    fi

    mkdir -p "$(dirname "$config")"

    # Check for disabled config and restore it
    if [ -f "${config}.disabled" ]; then
        mv "${config}.disabled" "$config"
        log_info "Restored $name (was disabled)"
        return 0
    fi

    if [ -f "$config" ]; then
        log_warn "$name already exists, skipping"
        return 0
    fi

    # Replace $PROJECT_DIR with actual path
    sed "s|\\\$PROJECT_DIR|$SCRIPT_DIR|g" "$example" > "$config"
    log_info "Created $name"
}

# ============================================================================
# SETUP COMMANDS
# ============================================================================

setup_claude() {
    echo ""
    echo -e "${BLUE}Setting up Claude Code...${NC}"
    echo ""
    create_config "$CLAUDE_EXAMPLE" "$CLAUDE_CONFIG" "Claude Code (.mcp.json)"
    echo ""
    echo "Next steps:"
    echo "  1. Restart Claude Code in this project"
    echo "  2. SSO login will open in browser"
    echo "  3. Test: ask Claude to list Airflow DAGs"
    echo "  4. Run: ./setup-mcp.sh vscode"
    echo ""
}

setup_vscode() {
    echo ""
    echo -e "${BLUE}Setting up VSCode Copilot...${NC}"
    echo ""
    create_config "$VSCODE_EXAMPLE" "$VSCODE_CONFIG" "VSCode (.vscode/mcp.json)"
    echo ""
    echo "Restart VSCode to load MCP."
    echo "SSO cookies are shared - no re-login needed."
    echo ""
}

setup_ampcode() {
    echo ""
    echo -e "${BLUE}Setting up AmpCode...${NC}"
    echo ""
    ampcode_add
    echo ""
    echo "Restart VSCode/AmpCode to load MCP."
    echo "SSO cookies are shared - no re-login needed."
    echo ""
}

setup_all() {
    echo ""
    echo -e "${BLUE}Setting up all tools...${NC}"
    echo ""
    create_config "$CLAUDE_EXAMPLE" "$CLAUDE_CONFIG" "Claude Code (.mcp.json)"
    create_config "$VSCODE_EXAMPLE" "$VSCODE_CONFIG" "VSCode (.vscode/mcp.json)"
    ampcode_add
    echo ""
    echo "Restart Claude Code first to trigger SSO login."
    echo "Other tools will reuse the saved cookies."
    echo ""
}

# ============================================================================
# TOGGLE COMMANDS (DISABLE/ENABLE)
# ============================================================================

disable_all() {
    echo ""
    echo -e "${BLUE}Disabling MCP configs...${NC}"
    echo ""

    local disabled=0

    if [ -f "$CLAUDE_CONFIG" ]; then
        mv "$CLAUDE_CONFIG" "${CLAUDE_CONFIG}.disabled"
        log_info "Disabled Claude Code"
        disabled=$((disabled + 1))
    fi

    if [ -f "$VSCODE_CONFIG" ]; then
        mv "$VSCODE_CONFIG" "${VSCODE_CONFIG}.disabled"
        log_info "Disabled VSCode Copilot"
        disabled=$((disabled + 1))
    fi

    if ampcode_exists && ! ampcode_is_disabled; then
        ampcode_disable
        disabled=$((disabled + 1))
    fi

    if [ $disabled -eq 0 ]; then
        log_warn "No configs to disable"
    else
        echo ""
        echo "Restart your tools - no MCP login prompts."
        echo "Run './setup-mcp.sh enable' to re-enable."
    fi
    echo ""
}

enable_all() {
    echo ""
    echo -e "${BLUE}Re-enabling MCP configs...${NC}"
    echo ""

    local enabled=0

    if [ -f "${CLAUDE_CONFIG}.disabled" ]; then
        mv "${CLAUDE_CONFIG}.disabled" "$CLAUDE_CONFIG"
        log_info "Enabled Claude Code"
        enabled=$((enabled + 1))
    fi

    if [ -f "${VSCODE_CONFIG}.disabled" ]; then
        mv "${VSCODE_CONFIG}.disabled" "$VSCODE_CONFIG"
        log_info "Enabled VSCode Copilot"
        enabled=$((enabled + 1))
    fi

    # Enable AmpCode if it exists and is disabled, or add if missing
    if ampcode_exists; then
        if ampcode_is_disabled; then
            ampcode_enable
            enabled=$((enabled + 1))
        fi
    else
        ampcode_add
        enabled=$((enabled + 1))
    fi

    if [ $enabled -eq 0 ]; then
        log_warn "No disabled configs found"
        echo "Run './setup-mcp.sh all' to create configs."
    else
        echo ""
        echo "Restart your tools to load MCP."
    fi
    echo ""
}

# ============================================================================
# MAIN - PARSE COMMAND
# ============================================================================

case "${1:-}" in
    claude)
        setup_claude
        ;;
    vscode)
        setup_vscode
        ;;
    ampcode|amp)
        setup_ampcode
        ;;
    rest)
        # Legacy alias
        setup_vscode
        setup_ampcode
        ;;
    all)
        setup_all
        show_status
        ;;
    disable|off)
        disable_all
        show_status
        ;;
    enable|on)
        enable_all
        show_status
        ;;
    status)
        show_status
        ;;
    *)
        show_help
        show_status
        ;;
esac
