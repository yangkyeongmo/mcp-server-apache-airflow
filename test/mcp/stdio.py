"""Launch the MCP server over stdio with the official Python client."""

from __future__ import annotations

import os
import shutil
import sys
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[2]


def server_environment(extra: Mapping[str, str] | None = None, *, inherit_venv: bool = True) -> dict[str, str]:
    """Build a child env that can import the server and reach Airflow when present."""
    env = get_default_environment()
    passthrough = [
        "UV_CACHE_DIR",
        "UV_PYTHON",
        "UV_PROJECT",
        "UV_PROJECT_ENVIRONMENT",
        "XDG_CACHE_HOME",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "no_proxy",
    ]
    if inherit_venv:
        passthrough.append("VIRTUAL_ENV")
    for key in passthrough:
        value = os.environ.get(key)
        if value:
            env[key] = value
    for key, value in os.environ.items():
        if key.startswith("AIRFLOW_"):
            env[key] = value
    env.setdefault("AIRFLOW_HOST", "http://127.0.0.1:8080")
    env.setdefault("AIRFLOW_USERNAME", "airflow")
    env.setdefault("AIRFLOW_PASSWORD", "airflow")
    env.setdefault("AIRFLOW_API_VERSION", "v1")
    if extra:
        env.update(dict(extra))
    return env


def default_server_command() -> tuple[str, list[str]]:
    uv = shutil.which("uv")
    if uv:
        return uv, ["run", "mcp-server-apache-airflow"]
    return sys.executable, ["-m", "src"]


@asynccontextmanager
async def mcp_stdio_session(
    *,
    cwd: str | Path | None = None,
    command: str | None = None,
    args: list[str] | None = None,
    env: Mapping[str, str] | None = None,
    inherit_venv: bool = True,
) -> AsyncIterator[ClientSession]:
    """Start `mcp-server-apache-airflow` on stdio and yield an initialized client session."""
    cmd, cmd_args = default_server_command()
    if command:
        cmd = command
        cmd_args = args or []
    elif args is not None:
        cmd_args = args
    params = StdioServerParameters(
        command=cmd,
        args=cmd_args,
        env=server_environment(env, inherit_venv=inherit_venv),
        cwd=str(cwd or REPO_ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


def parse_tool_payload(result: Any) -> Any:
    """Parse FastMCP text content, which is typically `str(dict)` rather than JSON."""
    import ast
    import json

    if getattr(result, "isError", False):
        raise AssertionError(f"MCP tool returned an error: {result}")
    content = getattr(result, "content", None) or []
    if not content:
        structured = getattr(result, "structuredContent", None)
        if structured is not None:
            return structured
        raise AssertionError(f"MCP tool returned no content: {result}")
    text = content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return text
