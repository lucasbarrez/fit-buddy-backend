from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel

# ... existing imports ... (Assuming I am appending or editing. I'll use replace_file_content safely)

class SetLogResponse(BaseModel):
    set_history_id: UUID
    message: str

class SessionStartResponse(BaseModel):
    session_history_id: UUID
    started_at: datetime
    message: str

class SessionStopResponse(BaseModel):
    session_history_id: UUID
    finished_at: Optional[datetime]
    duration_minutes: float
    total_xp: int
    message: str

class AvailabilityResponse(BaseModel):
    status: str
    wait_time: int
    dataset_source: str
    recommendation: str
    alternatives: List[dict] = []

# --- New Schemas ---

class SetHistorySchema(BaseModel):
    id: UUID
    exercise_id: UUID
    weight_kg: float
    reps_count: int
    rpe: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: UUID
    session_id: Optional[UUID]
    started_at: datetime
    finished_at: Optional[datetime]
    total_xp: int
    sets: List[SetHistorySchema]

class ExerciseHistoryStats(BaseModel):
    date: datetime
    weight_kg: float
    reps_count: int
    one_rep_max_est: float
