from uuid import UUID
from fastapi import HTTPException

from app.repositories.profile import ProfileRepository
from app.schemas.profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse


class ProfileService:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    async def get_current_profile(self, user_id: UUID) -> UserProfileResponse:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found. Please complete onboarding.")
        return profile

    async def create_profile(self, user_id: UUID, data: UserProfileCreate) -> UserProfileResponse:
        existing = await self.repo.get_by_user_id(user_id)
        if existing:
             raise HTTPException(status_code=400, detail="Profile already exists.")
             
        profile = await self.repo.create(
            user_id=user_id,
            onboarding=data.onboarding_data.model_dump(),
            stats=data.current_stats.model_dump()
        )
        return profile

    async def update_profile(self, user_id: UUID, data: UserProfileUpdate) -> UserProfileResponse:
        updated = await self.repo.update(
            user_id=user_id,
            onboarding=data.onboarding_data.model_dump() if data.onboarding_data else None,
            stats=data.current_stats.model_dump() if data.current_stats else None
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Profile not found")
        return updated
