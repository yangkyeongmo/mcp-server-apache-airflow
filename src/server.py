from fastmcp import FastMCP

from src.routes import register_routes

app = FastMCP("mcp-apache-airflow")

register_routes(app)
