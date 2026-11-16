#!/usr/bin/env bash
# Dump tools/list from this checkout and from origin/main, then apply MCP schema rules.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CURRENT_DUMP="${CURRENT_DUMP:-/tmp/mcp-pr-tools.json}"
BASELINE_DUMP="${BASELINE_DUMP:-/tmp/mcp-main-tools.json}"
SNAPSHOT="${SNAPSHOT:-$ROOT/test/mcp/tools_snapshot.json}"
MAIN_SRC="${MAIN_SRC:-/tmp/mcp-main-src}"
MAIN_REF="${MAIN_REF:-origin/main}"

echo "::group::Dump tools/list from this branch"
uv run python scripts/dump_mcp_tools.py --out "$CURRENT_DUMP"
echo "::endgroup::"

echo "::group::Check committed snapshot"
uv run python scripts/mcp_compat_check.py --current "$CURRENT_DUMP" --snapshot "$SNAPSHOT"
echo "::endgroup::"

echo "::group::Dump tools/list from ${MAIN_REF}"
git fetch --no-tags origin main
if git worktree list --porcelain | grep -q "^worktree ${MAIN_SRC}$"; then
  git worktree remove --force "$MAIN_SRC"
fi
rm -rf "$MAIN_SRC"
git worktree add "$MAIN_SRC" "$MAIN_REF"
(
  cd "$MAIN_SRC"
  uv sync --dev
)
uv run python scripts/dump_mcp_tools.py --cwd "$MAIN_SRC" --no-inherit-venv --out "$BASELINE_DUMP"
echo "::endgroup::"

echo "::group::Compatibility diff vs main"
uv run python scripts/mcp_compat_check.py --current "$CURRENT_DUMP" --baseline "$BASELINE_DUMP"
echo "::endgroup::"
