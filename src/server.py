from typing import List

from fastmcp import FastMCP, settings
from fastmcp.exceptions import ToolError
from fastmcp.tools import Tool
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request

from starlette.requests import Request

from src.airflow.airflow_client import api_client


class UserTokenHandler(Middleware):
    async def on_call_tool(
            self,
            context: MiddlewareContext,
            call_next
        ):
        """
        Executed on every tool call.
        We intercept it with goal to get secure token
        if it is in the header
        """

        print(f"Raw middleware processing: {context.method}")

        self.set_jwt_token()

        result = await call_next(context)
        print(f"Raw middleware completed: {context.method}")
        return result

    def set_jwt_token(self):
        request : Request = get_http_request()

        auth_header = request.headers.get("Authorization")

        if auth_header:
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1].strip()
                if not token:
                    raise ToolError(
                        "Unauthorized: Empty Bearer token",
                    )
                print(f"Got Bearer JWT token: {token}")

                api_client.configuration.access_token = token
            if auth_header.startswith("Basic "): 
                base64_str = auth_header.split(" ", 1)[1].strip()
                if not base64_str:
                    raise ToolError(
                        "Unauthorized: Empty base64 string for basic authorization",
                    )
                print(f"Got base64 string: {base64_str}")

                api_client.default_headers["Authorization"] = f"Basic {base64_str}"


class MCPServer:

    DEFAULT_TRANSPORT = "stdio"
    DEFAULT_HOST = settings.host
    DEFAULT_PORT = settings.port

    def __init__(self, transport: str, host: str, port: int):
        self._transport = transport
        self._host = host
        self._port = port

        self._mcp = FastMCP(
                "airflow-mcp",
                host=host,
                port=port
            )

        if transport == 'http':
            self._mcp.add_middleware(UserTokenHandler())

    def add_tools(self, tools: List[Tool]):
        for tool in tools:
            self._mcp.add_tool(tool)

    def run(self):
        self._mcp.run(transport=self._transport)
