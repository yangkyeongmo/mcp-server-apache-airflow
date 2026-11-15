"""Launch the MCP server over stdio with the official Python client."""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client

# apache-airflow-client to_dict() is emitted via str(), which includes datetime.datetime(...).
_DATETIME_REPR = re.compile(r"datetime\.datetime\((?:[^()]|\([^()]*\))*\)")

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
    stdio_cm = stdio_client(params)
    read, write = await stdio_cm.__aenter__()
    session = ClientSession(read, write)
    try:
        await session.__aenter__()
        await session.initialize()
        yield session
    finally:
        await _aclose_quietly(session)
        await _aclose_quietly(stdio_cm)


async def _aclose_quietly(context: Any) -> None:
    try:
        await context.__aexit__(None, None, None)
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise


def parse_client_text(text: str) -> Any:
    """Parse MCP tool text: JSON, Python literals, or airflow-client datetime reprs."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError, MemoryError):
        pass
    rewritten = _DATETIME_REPR.sub('"1970-01-01T00:00:00"', text)
    try:
        return ast.literal_eval(rewritten)
    except (SyntaxError, ValueError, MemoryError):
        return text


def parse_tool_payload(result: Any) -> Any:
    """Parse FastMCP text content, which is typically `str(dict)` rather than JSON."""
    if getattr(result, "isError", False):
        raise AssertionError(f"MCP tool returned an error: {result}")
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict) and structured:
        if "result" in structured and len(structured) == 1:
            return structured["result"]
        return structured
    content = getattr(result, "content", None) or []
    if not content:
        raise AssertionError(f"MCP tool returned no content: {result}")
    return parse_client_text(content[0].text)
