#!/usr/bin/env python3
"""Dump MCP tools/list (name + inputSchema) from a stdio server."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from test.mcp.compat import dump_from_list_tools, write_snapshot  # noqa: E402
from test.mcp.stdio import mcp_stdio_session  # noqa: E402


async def dump_tools(
    *,
    cwd: Path,
    command: str | None,
    args: list[str] | None,
    inherit_venv: bool,
) -> dict:
    async with mcp_stdio_session(
        cwd=cwd,
        command=command,
        args=args,
        inherit_venv=inherit_venv,
    ) as session:
        result = await session.list_tools()
        return dump_from_list_tools(result.tools)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Write JSON snapshot to this path")
    parser.add_argument("--cwd", default=str(REPO_ROOT), help="Working directory of the MCP server")
    parser.add_argument("--command", default=None, help="Server executable (default: uv run mcp-server-apache-airflow)")
    parser.add_argument(
        "--arg",
        dest="args",
        action="append",
        default=None,
        help="Server argument (repeatable). Used with --command.",
    )
    parser.add_argument(
        "--no-inherit-venv",
        action="store_true",
        help="Do not pass VIRTUAL_ENV into the server (use when dumping another checkout)",
    )
    args = parser.parse_args()
    payload = asyncio.run(
        dump_tools(
            cwd=Path(args.cwd),
            command=args.command,
            args=args.args,
            inherit_venv=not args.no_inherit_venv,
        )
    )
    write_snapshot(payload, args.out)
    print(f"Wrote {len(payload.get('tools') or {})} tools to {args.out}", file=sys.stderr)
    print(json.dumps({"tool_count": len(payload.get("tools") or {}), "names": sorted(payload.get("tools") or {})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
