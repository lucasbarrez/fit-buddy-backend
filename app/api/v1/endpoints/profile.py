from typing import Any
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user_db import get_db

from app.schemas.common import SuccessResponse
from app.schemas.profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from app.repositories.profile import ProfileRepository
from app.services.profile import ProfileService

# Mock Auth Dependency until Supabase Auth is fully integrated
# We assume the token sets request.state.user or similar, 
# but for now we'll mock a dependency that returns a fixed user_id or extracts from header
from app.api.dependencies import get_current_user # Re-use existing which returns dict

router = APIRouter()

async def get_profile_service(session: AsyncSession = Depends(get_db)) -> ProfileService:
    repo = ProfileRepository(session)
    return ProfileService(repo)


@router.post("/onboarding", response_model=SuccessResponse[UserProfileResponse])
async def complete_onboarding(
    data: UserProfileCreate,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> Any:
    """
    Complete initial onboarding (create profile).
    """
    user_id = current_user["id"]
    profile = await service.create_profile(user_id, data)
    return SuccessResponse(data=profile, message="Onboarding completed successfully")


@router.get("/me", response_model=SuccessResponse[UserProfileResponse])
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> Any:
    """
    Get current user profile details.
    """
    user_id = current_user["id"]
    profile = await service.get_current_profile(user_id)
    return SuccessResponse(data=profile)


@router.patch("/me", response_model=SuccessResponse[UserProfileResponse])
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> Any:
    """
    Update profile data.
    """
    user_id = current_user["id"]
    profile = await service.update_profile(user_id, data)
    return SuccessResponse(data=profile, message="Profile updated")
