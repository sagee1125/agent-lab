from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """所有自訂業務錯誤的基底。"""

    status_code = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
