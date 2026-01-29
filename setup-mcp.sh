#!/bin/bash
# Setup script to sync MCP Airflow config to Claude Code, AmpCode, and VSCode Copilot
#
# Usage:
#   ./setup-mcp.sh           # Show help
#   ./setup-mcp.sh claude    # Enable for Claude Code only
#   ./setup-mcp.sh amp       # Enable for AmpCode only
#   ./setup-mcp.sh vscode    # Enable for VSCode Copilot only
#   ./setup-mcp.sh all       # Enable for all tools
#   ./setup-mcp.sh disable   # Disable for all tools

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLE_CONFIG="$SCRIPT_DIR/mcp-settings.example.json"
MASTER_CONFIG="$SCRIPT_DIR/mcp-settings.json"

# Config paths
CLAUDE_CODE_CONFIG="$HOME/.claude/settings.json"
AMPCODE_CONFIG="$HOME/.config/amp/settings.json"
VSCODE_MCP="$SCRIPT_DIR/.vscode/mcp.json"
PROJECT_MCP="$SCRIPT_DIR/.mcp.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    echo ""
    echo -e "${BLUE}Airflow MCP Server - Setup Script${NC}"
    echo ""
    echo "Usage: ./setup-mcp.sh <command>"
    echo ""
    echo "Commands:"
    echo "  claude    Enable Airflow MCP for Claude Code"
    echo "  amp       Enable Airflow MCP for AmpCode"
    echo "  vscode    Enable Airflow MCP for VSCode Copilot"
    echo "  all       Enable for all tools"
    echo "  disable   Disable for all tools"
    echo "  status    Show current status"
    echo ""
    echo "After enabling, restart the tool and complete SSO login."
    echo ""
}

# Check dependencies
check_deps() {
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Install with: brew install jq"
        exit 1
    fi
}

# Create personal config from example if needed
ensure_master_config() {
    if [ ! -f "$EXAMPLE_CONFIG" ]; then
        log_error "Example config not found: $EXAMPLE_CONFIG"
        exit 1
    fi

    if [ ! -f "$MASTER_CONFIG" ]; then
        log_info "Creating personal config from example..."
        sed "s|/path/to/mcp-server-apache-airflow|$SCRIPT_DIR|g" "$EXAMPLE_CONFIG" > "$MASTER_CONFIG"
        log_info "Created: $MASTER_CONFIG"
    fi
}

# Get MCP servers JSON
get_mcp_servers() {
    jq '.mcpServers' "$MASTER_CONFIG"
}

# Enable for Claude Code
enable_claude() {
    log_info "Enabling Airflow MCP for Claude Code..."

    mkdir -p "$(dirname "$CLAUDE_CODE_CONFIG")"

    if [ ! -f "$CLAUDE_CODE_CONFIG" ]; then
        echo '{}' > "$CLAUDE_CODE_CONFIG"
    fi

    local servers
    servers=$(get_mcp_servers)

    jq --argjson srv "$servers" '.mcpServers = (.mcpServers // {}) + $srv' "$CLAUDE_CODE_CONFIG" > "${CLAUDE_CODE_CONFIG}.tmp"
    mv "${CLAUDE_CODE_CONFIG}.tmp" "$CLAUDE_CODE_CONFIG"

    # Also create project-level .mcp.json symlink
    rm -f "$PROJECT_MCP"
    ln -s "$(basename "$MASTER_CONFIG")" "$PROJECT_MCP"

    log_info "Enabled: $CLAUDE_CODE_CONFIG"
    log_info "Enabled: $PROJECT_MCP"
    echo ""
    echo -e "${YELLOW}Next: Restart Claude Code, then SSO login will trigger${NC}"
}

# Enable for AmpCode
enable_amp() {
    log_info "Enabling Airflow MCP for AmpCode..."

    mkdir -p "$(dirname "$AMPCODE_CONFIG")"

    if [ ! -f "$AMPCODE_CONFIG" ]; then
        echo '{}' > "$AMPCODE_CONFIG"
    fi

    local servers
    servers=$(get_mcp_servers)

    jq --argjson srv "$servers" '.mcpServers = (.mcpServers // {}) + $srv' "$AMPCODE_CONFIG" > "${AMPCODE_CONFIG}.tmp"
    mv "${AMPCODE_CONFIG}.tmp" "$AMPCODE_CONFIG"

    log_info "Enabled: $AMPCODE_CONFIG"
    echo ""
    echo -e "${YELLOW}Next: Restart AmpCode, then SSO login will trigger${NC}"
}

# Enable for VSCode Copilot
enable_vscode() {
    log_info "Enabling Airflow MCP for VSCode Copilot..."

    mkdir -p "$(dirname "$VSCODE_MCP")"

    local servers
    servers=$(get_mcp_servers)

    jq -n --argjson srv "$servers" '{ "servers": $srv }' > "$VSCODE_MCP"

    log_info "Enabled: $VSCODE_MCP"
    echo ""
    echo -e "${YELLOW}Next: Open this folder in VSCode, Copilot will load MCP${NC}"
}

# Disable for all tools
disable_all() {
    log_info "Disabling Airflow MCP for all tools..."

    # Claude Code
    if [ -f "$CLAUDE_CODE_CONFIG" ]; then
        jq 'del(.mcpServers["airflow-sso"])' "$CLAUDE_CODE_CONFIG" > "${CLAUDE_CODE_CONFIG}.tmp"
        mv "${CLAUDE_CODE_CONFIG}.tmp" "$CLAUDE_CODE_CONFIG"
        log_info "Disabled in Claude Code"
    fi

    # AmpCode
    if [ -f "$AMPCODE_CONFIG" ]; then
        jq 'del(.mcpServers["airflow-sso"])' "$AMPCODE_CONFIG" > "${AMPCODE_CONFIG}.tmp"
        mv "${AMPCODE_CONFIG}.tmp" "$AMPCODE_CONFIG"
        log_info "Disabled in AmpCode"
    fi

    # VSCode
    if [ -f "$VSCODE_MCP" ]; then
        rm -f "$VSCODE_MCP"
        log_info "Disabled in VSCode Copilot"
    fi

    # Project-level
    if [ -f "$PROJECT_MCP" ]; then
        rm -f "$PROJECT_MCP"
        log_info "Disabled project .mcp.json"
    fi

    echo ""
    log_info "All tools disabled. Restart each tool for changes to take effect."
}

# Show status
show_status() {
    echo ""
    echo -e "${BLUE}Airflow MCP Status${NC}"
    echo ""

    # Claude Code
    if [ -f "$CLAUDE_CODE_CONFIG" ] && jq -e '.mcpServers["airflow-sso"]' "$CLAUDE_CODE_CONFIG" > /dev/null 2>&1; then
        echo -e "Claude Code:    ${GREEN}ENABLED${NC}"
    else
        echo -e "Claude Code:    ${RED}DISABLED${NC}"
    fi

    # AmpCode
    if [ -f "$AMPCODE_CONFIG" ] && jq -e '.mcpServers["airflow-sso"]' "$AMPCODE_CONFIG" > /dev/null 2>&1; then
        echo -e "AmpCode:        ${GREEN}ENABLED${NC}"
    else
        echo -e "AmpCode:        ${RED}DISABLED${NC}"
    fi

    # VSCode
    if [ -f "$VSCODE_MCP" ]; then
        echo -e "VSCode Copilot: ${GREEN}ENABLED${NC}"
    else
        echo -e "VSCode Copilot: ${RED}DISABLED${NC}"
    fi

    # Project
    if [ -f "$PROJECT_MCP" ]; then
        echo -e "Project .mcp:   ${GREEN}ENABLED${NC}"
    else
        echo -e "Project .mcp:   ${RED}DISABLED${NC}"
    fi

    echo ""
}

# Main
check_deps

case "${1:-}" in
    claude)
        ensure_master_config
        enable_claude
        ;;
    amp)
        ensure_master_config
        enable_amp
        ;;
    vscode)
        ensure_master_config
        enable_vscode
        ;;
    all)
        ensure_master_config
        enable_claude
        enable_amp
        enable_vscode
        ;;
    disable)
        disable_all
        ;;
    status)
        show_status
        ;;
    *)
        show_help
        show_status
        ;;
esac
