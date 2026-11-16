#!/usr/bin/env python3
"""Compare MCP tools/list dumps: snapshot freshness and breaking-change rules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from test.mcp.compat import (  # noqa: E402
    compatibility_diff,
    format_findings,
    load_snapshot,
    snapshot_matches,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", required=True, help="tools/list dump from this branch")
    parser.add_argument("--snapshot", help="Committed snapshot that current must match")
    parser.add_argument("--baseline", help="tools/list dump from main (compatibility rules)")
    args = parser.parse_args()

    current = load_snapshot(args.current)
    exit_code = 0

    if args.snapshot:
        errors = snapshot_matches(current, load_snapshot(args.snapshot))
        if errors:
            print("Snapshot check failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            print(
                "Regenerate with: uv run python scripts/dump_mcp_tools.py --out test/mcp/tools_snapshot.json",
                file=sys.stderr,
            )
            exit_code = 1
        else:
            print(f"Snapshot matches ({len(current.get('tools') or {})} tools).")

    if args.baseline:
        findings = compatibility_diff(load_snapshot(args.baseline), current)
        print(format_findings(findings))
        additions = sorted(set((current.get("tools") or {})) - set((load_snapshot(args.baseline).get("tools") or {})))
        if additions:
            print(f"Allowed additions (new tools): {additions}")
        if findings:
            exit_code = 1

    if not args.snapshot and not args.baseline:
        parser.error("provide --snapshot and/or --baseline")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
