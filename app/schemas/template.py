from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ExerciseTemplate(BaseModel):
    muscle_group: str
    pattern: str = Field(..., description="Movement pattern e.g., Squat, Hinge, Push")
    default_exercise: str = Field(..., description="Default exercise name")
    sets: int
    reps: int | str = Field(..., description="Reps count or range string like '12-15'")
    rest: int = Field(..., description="Rest in seconds")
    rpe_target: Optional[int] = None
    duration: Optional[int] = Field(None, description="Duration in seconds for static holds")
    notes: Optional[str] = None

class SessionTemplate(BaseModel):
    name_template: str
    description_template: str
    duration_minutes: int
    exercises: List[ExerciseTemplate]

class PhaseTemplate(BaseModel):
    name: str
    weeks: int
    focus: str
    progression: str

class ProgramTemplate(BaseModel):
    name_template: str
    description_template: str
    goal: Literal["muscle_gain", "weight_loss", "strength", "endurance", "flexibility", "general_fitness"]
    level: Literal["beginner", "intermediate", "advanced"]
    phases: List[PhaseTemplate]
    default_days_per_week: int
    sessions: List[SessionTemplate]
