from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# --- Session Schemas ---
class SessionExerciseRead(BaseModel):
    exercise_id: Optional[UUID] = None
    exercise_name: str
    target_sets: int
    target_reps: int
    rest_seconds: int
    notes: Optional[str] = None

class SessionRead(BaseModel):
    id: UUID
    name: str
    order_index: int
    exercises_plan: List[SessionExerciseRead]
    
    model_config = ConfigDict(from_attributes=True)

# --- Program Schemas ---
class ProgramRead(BaseModel):
    id: UUID
    name: str
    goal: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    sessions: List[SessionRead] = []
    
    model_config = ConfigDict(from_attributes=True)

class ProgramGenerateResponse(BaseModel):
    program: ProgramRead
    message: str
