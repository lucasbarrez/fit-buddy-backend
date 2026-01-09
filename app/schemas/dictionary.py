from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# --- Machine Schemas ---
class MachineRead(BaseModel):
    id: UUID
    name: str
    machine_type_id: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# --- Exercise Schemas ---
class ExerciseRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    muscle_group: str
    machine_type_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
