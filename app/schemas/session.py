from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# --- Availability Check ---

class AlternativeExercise(BaseModel):
    type: str # 'db_link' or 'rag_suggestion'
    exercise: str
    id: str
    wait_time: Any

class AvailabilityResponse(BaseModel):
    status: str # 'available' or 'busy'
    wait_time: int
    recommendation: str
    alternatives: Optional[List[AlternativeExercise]] = None
    dataset_source: str

# --- Tracking ---

class SessionStartRequest(BaseModel):
    program_id: UUID
    session_id: UUID # The planned session ID (template)

class SessionStartResponse(BaseModel):
    session_history_id: UUID
    started_at: datetime
    message: str

class SetLogRequest(BaseModel):
    session_history_id: UUID
    exercise_id: UUID
    weight_kg: float
    reps_count: int
    rpe: Optional[int] = Field(None, ge=1, le=10)
    machine_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
class SetLogResponse(BaseModel):
    set_history_id: UUID
    message: str

class SessionStopRequest(BaseModel):
    session_history_id: UUID
    feedback_notes: Optional[str] = None

class SessionStopResponse(BaseModel):
    session_history_id: UUID
    finished_at: datetime
    duration_minutes: float
    total_xp: int
    message: str

class SetHistoryItem(BaseModel):
    id: UUID
    exercise_id: UUID
    weight_kg: float
    reps_count: int
    rpe: Optional[int]
    timestamp: datetime = Field(alias="end_time")
    sensor_snapshot: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: UUID
    session_id: Optional[UUID]
    started_at: datetime
    finished_at: Optional[datetime]
    total_xp: int
    sets: List[SetHistoryItem]

class ExerciseStatsResponse(BaseModel):
    date: datetime
    weight_kg: float
    reps_count: int
    one_rep_max_est: float
