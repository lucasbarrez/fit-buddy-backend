"""
API dependencies for Better Auth session verification
"""

from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.logging import app_logger
from app.core.security import verify_session_token

# Security scheme for Swagger UI - enables the 🔓 Authorize button
security = HTTPBearer(
    auto_error=False,
    description="Better Auth session token (get from cookie: better-auth.session_token)",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """
    Get current user from Better Auth session token

    If DISABLE_AUTH=True (development), returns a mock user without verification.

    Architecture:
    1. Client → FastAPI: Authorization: Bearer <better-auth-session-token>
    2. FastAPI → Better Auth API: Verify session
    3. Better Auth returns user data if valid
    4. FastAPI uses user data

    Args:
        credentials: HTTP Bearer credentials (Better Auth session token)

    Returns:
        User data dict with: id, email, name, role, etc.

    Raises:
        UnauthorizedException: If session is missing, invalid, or expired
    """
    # Development mode: Skip auth if DISABLE_AUTH=True
    if settings.DISABLE_AUTH:
        app_logger.warning("⚠️  AUTH DISABLED - Using mock user for development")
        return {
            "id": "dev-user-123",
            "email": "dev@example.com",
            "name": "Dev User",
            "role": "user",
            "email_verified": True,
        }

    if not credentials:
        raise UnauthorizedException(
            message="Authorization header missing",
            details={"hint": "Send Better Auth session token via Authorization: Bearer <token>"},
        )

    # credentials.credentials contains the session token
    user = await verify_session_token(credentials.credentials)

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any] | None:
    """
    Get current user if Better Auth session is provided, otherwise return None

    Useful for endpoints that work for both authenticated and non-authenticated users.
    If session is invalid/expired, returns None instead of raising an exception.

    Args:
        credentials: Optional HTTP Bearer credentials (Better Auth session token)

    Returns:
        User data dict if session is valid, None otherwise
    """
    if settings.DISABLE_AUTH:
        return None

    if not credentials:
        return None

    try:
        # Try to verify the session, return None if it fails
        return await verify_session_token(credentials.credentials)
    except UnauthorizedException:
        # Session is invalid/expired, return None for optional auth
        app_logger.debug("Invalid session in optional auth endpoint - returning None")
        return None
