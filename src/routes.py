from starlette.requests import Request
from starlette.responses import JSONResponse


def register_routes(app):
    @app.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    return health_check
