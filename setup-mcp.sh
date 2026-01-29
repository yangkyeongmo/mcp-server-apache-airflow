#!/bin/bash
# Setup script to create personal MCP configs from examples
#
# Usage:
#   ./setup-mcp.sh claude   # Step 1: Setup Claude Code, then SSO login & test
#   ./setup-mcp.sh rest     # Step 2: Setup AmpCode + VSCode (reuses SSO cookies)
#   ./setup-mcp.sh all      # Setup all at once
#   ./setup-mcp.sh disable  # Disable all MCP configs (no login prompts)
#   ./setup-mcp.sh enable   # Re-enable all MCP configs
#   ./setup-mcp.sh status   # Show current status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Config files
CLAUDE_EXAMPLE="$SCRIPT_DIR/.mcp.example.json"
CLAUDE_CONFIG="$SCRIPT_DIR/.mcp.json"

AMP_EXAMPLE="$SCRIPT_DIR/.amp/settings.example.json"
AMP_CONFIG="$SCRIPT_DIR/.amp/settings.json"

VSCODE_EXAMPLE="$SCRIPT_DIR/.vscode/mcp.example.json"
VSCODE_CONFIG="$SCRIPT_DIR/.vscode/mcp.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

show_help() {
    echo ""
    echo -e "${BLUE}Airflow MCP Setup${NC}"
    echo ""
    echo "Setup commands:"
    echo "  claude   Setup Claude Code only"
    echo "  rest     Setup AmpCode + VSCode (after SSO login)"
    echo "  all      Setup all tools at once"
    echo ""
    echo "Toggle commands:"
    echo "  disable  Disable MCP (avoid login prompts when not on VPN)"
    echo "  enable   Re-enable MCP configs"
    echo "  status   Show current config status"
    echo ""
}

show_status() {
    echo ""
    echo -e "${BLUE}Config Status${NC}"
    echo ""

    # Claude Code
    if [ -f "$CLAUDE_CONFIG" ]; then
        echo -e "  Claude Code  (.mcp.json)            ${GREEN}enabled${NC}"
    elif [ -f "${CLAUDE_CONFIG}.disabled" ]; then
        echo -e "  Claude Code  (.mcp.json)            ${RED}disabled${NC}"
    else
        echo -e "  Claude Code  (.mcp.json)            ${YELLOW}not setup${NC}"
    fi

    # AmpCode
    if [ -f "$AMP_CONFIG" ]; then
        echo -e "  AmpCode      (.amp/settings.json)   ${GREEN}enabled${NC}"
    elif [ -f "${AMP_CONFIG}.disabled" ]; then
        echo -e "  AmpCode      (.amp/settings.json)   ${RED}disabled${NC}"
    else
        echo -e "  AmpCode      (.amp/settings.json)   ${YELLOW}not setup${NC}"
    fi

    # VSCode
    if [ -f "$VSCODE_CONFIG" ]; then
        echo -e "  VSCode       (.vscode/mcp.json)     ${GREEN}enabled${NC}"
    elif [ -f "${VSCODE_CONFIG}.disabled" ]; then
        echo -e "  VSCode       (.vscode/mcp.json)     ${RED}disabled${NC}"
    else
        echo -e "  VSCode       (.vscode/mcp.json)     ${YELLOW}not setup${NC}"
    fi

    # SSO cookies
    if [ -d "$SCRIPT_DIR/.airflow_state" ]; then
        echo ""
        echo -e "  SSO cookies  (.airflow_state/)      ${GREEN}saved${NC}"
    else
        echo ""
        echo -e "  SSO cookies  (.airflow_state/)      ${YELLOW}not yet${NC}"
    fi

    echo ""
}

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

    sed "s|\\\$PROJECT_DIR|$SCRIPT_DIR|g" "$example" > "$config"
    log_info "Created $name"
}

setup_claude() {
    echo ""
    echo -e "${BLUE}Setting up Claude Code...${NC}"
    echo ""
    create_config "$CLAUDE_EXAMPLE" "$CLAUDE_CONFIG" "Claude Code (.mcp.json)"
    echo ""
    echo "Next steps:"
    echo "  1. Restart Claude Code"
    echo "  2. SSO login will open in browser"
    echo "  3. Test: ask Claude to list Airflow DAGs"
    echo "  4. Run: ./setup-mcp.sh rest"
    echo ""
}

setup_rest() {
    echo ""
    echo -e "${BLUE}Setting up AmpCode + VSCode...${NC}"
    echo ""
    create_config "$AMP_EXAMPLE" "$AMP_CONFIG" "AmpCode (.amp/settings.json)"
    create_config "$VSCODE_EXAMPLE" "$VSCODE_CONFIG" "VSCode (.vscode/mcp.json)"
    echo ""
    echo "Restart AmpCode and VSCode to load MCP."
    echo "SSO cookies are shared - no re-login needed."
    echo ""
}

setup_all() {
    echo ""
    echo -e "${BLUE}Setting up all tools...${NC}"
    echo ""
    create_config "$CLAUDE_EXAMPLE" "$CLAUDE_CONFIG" "Claude Code (.mcp.json)"
    create_config "$AMP_EXAMPLE" "$AMP_CONFIG" "AmpCode (.amp/settings.json)"
    create_config "$VSCODE_EXAMPLE" "$VSCODE_CONFIG" "VSCode (.vscode/mcp.json)"
    echo ""
    echo "Restart Claude Code first to trigger SSO login."
    echo "Other tools will reuse the saved cookies."
    echo ""
}

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

    if [ -f "$AMP_CONFIG" ]; then
        mv "$AMP_CONFIG" "${AMP_CONFIG}.disabled"
        log_info "Disabled AmpCode"
        disabled=$((disabled + 1))
    fi

    if [ -f "$VSCODE_CONFIG" ]; then
        mv "$VSCODE_CONFIG" "${VSCODE_CONFIG}.disabled"
        log_info "Disabled VSCode"
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

    if [ -f "${AMP_CONFIG}.disabled" ]; then
        mv "${AMP_CONFIG}.disabled" "$AMP_CONFIG"
        log_info "Enabled AmpCode"
        enabled=$((enabled + 1))
    fi

    if [ -f "${VSCODE_CONFIG}.disabled" ]; then
        mv "${VSCODE_CONFIG}.disabled" "$VSCODE_CONFIG"
        log_info "Enabled VSCode"
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

case "${1:-}" in
    claude)
        setup_claude
        ;;
    rest)
        setup_rest
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
