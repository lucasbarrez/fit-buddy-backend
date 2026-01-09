import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import app_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all the requests"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        client_host = request.client.host if request.client else "unknown"

        app_logger.info(f"→ {request.method} {request.url.path} from {client_host}")

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            app_logger.info(
                f"← {request.method} {request.url.path} "
                f"[{response.status_code}] {duration:.3f}s"
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            app_logger.error(
                f"✗ {request.method} {request.url.path} " f"FAILED after {duration:.3f}s: {str(e)}"
            )
            raise
