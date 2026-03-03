from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

app = FastMCP("mcp-apache-airflow")


@app.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})
