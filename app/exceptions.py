from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundException(Exception):
    def __init__(self, detail: str = "Recurso no encontrado"):
        self.detail = detail


class BadRequestException(Exception):
    def __init__(self, detail: str = "Solicitud invalida"):
        self.detail = detail


class ForbiddenException(Exception):
    def __init__(self, detail: str = "Acceso denegado"):
        self.detail = detail


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content={"detail": exc.detail},
        )

    @app.exception_handler(BadRequestException)
    async def bad_request_handler(request: Request, exc: BadRequestException):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.detail},
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_handler(request: Request, exc: ForbiddenException):
        return JSONResponse(
            status_code=403,
            content={"detail": exc.detail},
        )
