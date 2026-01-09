"""
Exception handlers for the application
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.logging import app_logger
from app.schemas.common import ErrorDetail, ErrorResponse


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom app exceptions"""
        app_logger.error(
            f"AppException: {exc.message} | "
            f"Status: {exc.status_code} | "
            f"Path: {request.url.path} | "
            f"Details: {exc.details}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=exc.message, status_code=exc.status_code, details=exc.details
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        app_logger.error(
            f"HTTPException: {exc.detail} | "
            f"Status: {exc.status_code} | "
            f"Path: {request.url.path}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=str(exc.detail), status_code=exc.status_code
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors"""
        errors = [
            ErrorDetail(
                field=".".join(str(loc) for loc in error["loc"]),
                message=error["msg"],
                type=error["type"],
            )
            for error in exc.errors()
        ]

        app_logger.error(
            f"ValidationError: {len(errors)} errors | "
            f"Path: {request.url.path} | "
            f"Errors: {errors}"
        )

        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                message="Validation error", status_code=422, errors=errors
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions"""
        app_logger.exception(f"Unexpected error: {str(exc)} | " f"Path: {request.url.path}")

        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error",
                status_code=500,
                details={"error": str(exc)} if app.debug else None,
            ).model_dump(),
        )
