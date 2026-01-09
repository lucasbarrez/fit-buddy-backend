from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import UserProfile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def create(self, user_id: UUID, onboarding: dict, stats: dict) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            onboarding_data=onboarding,
            current_stats=stats
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update(self, user_id: UUID, onboarding: dict = None, stats: dict = None) -> Optional[UserProfile]:
        # Construct update values
        values = {}
        if onboarding:
            values["onboarding_data"] = onboarding
        if stats:
            values["current_stats"] = stats
            
        if not values:
            return await self.get_by_user_id(user_id)

        query = (
            update(UserProfile)
            .where(UserProfile.user_id == user_id)
            .values(**values)
            .returning(UserProfile)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().one_or_none()
