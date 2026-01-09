"""
FastAPI application entry point
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import app_logger
from app.middleware.cors import setup_cors
from app.middleware.error_handlers import setup_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events"""
    # Startup
    app_logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    app_logger.info(f"Environment: {settings.ENVIRONMENT}")
    app_logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    app_logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    # Setup CORS
    setup_cors(app)

    # Setup middlewares
    app.add_middleware(LoggingMiddleware)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Setup rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


# Create app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
