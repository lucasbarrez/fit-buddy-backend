"""
Example protected endpoint using Supabase Auth
"""

from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_optional_user
from app.schemas.common import SuccessResponse

router = APIRouter()


@router.get("/me", response_model=SuccessResponse[dict[str, Any]])
async def get_current_user_info(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SuccessResponse[dict[str, Any]]:
    """
    Get current authenticated user information

    This endpoint requires authentication via Better Auth/Supabase Auth.
    Send the JWT token in the Authorization header: Bearer <token>
    """
    return SuccessResponse(message="User retrieved successfully", data=current_user)


@router.get("/public-or-private")
async def public_or_private_route(
    current_user: dict[str, Any] | None = Depends(get_optional_user),
) -> dict:
    """
    Example endpoint that works for both authenticated and non-authenticated users
    """
    if current_user:
        return {
            "message": f"Hello {current_user.get('email', 'user')}!",
            "authenticated": True,
            "user_id": current_user["id"],
        }
    else:
        return {"message": "Hello guest!", "authenticated": False}
