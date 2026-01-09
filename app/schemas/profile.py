from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# --- JSON Structure for Onboarding ---
class OnboardingData(BaseModel):
    goal: Literal["weight_loss", "muscle_gain", "endurance", "flexibility"]
    experience_level: Literal["beginner", "intermediate", "advanced"]
    equipment: List[str] = Field(default_factory=list) # "dumbbell", "barbell", "bench", "machine"
    injuries: List[str] = Field(default_factory=list)
    days_per_week: int = Field(ge=1, le=7, default=3)
    session_duration_minutes: int = Field(ge=15, le=180, default=60)

# --- JSON Structure for Stats ---
class PhysicsStats(BaseModel):
    weight_kg: float
    height_cm: float
    body_fat_percentage: Optional[float] = None
    age: int


# --- API Models ---

class UserProfileCreate(BaseModel):
    onboarding_data: OnboardingData
    current_stats: PhysicsStats

class UserProfileUpdate(BaseModel):
    onboarding_data: Optional[OnboardingData] = None
    current_stats: Optional[PhysicsStats] = None

class UserProfileResponse(BaseModel):
    user_id: UUID
    onboarding_data: OnboardingData
    current_stats: PhysicsStats
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
