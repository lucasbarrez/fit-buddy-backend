from typing import List, Optional

from app.repositories.dictionary import DictionaryRepository
from app.schemas.dictionary import MachineRead, ExerciseRead


class DictionaryService:
    def __init__(self, repo: DictionaryRepository):
        self.repo = repo

    async def list_machines(self) -> List[MachineRead]:
        return await self.repo.get_machines()

    async def list_exercises(
        self, 
        muscle_group: Optional[str] = None, 
        machine_type_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExerciseRead]:
        return await self.repo.get_exercises(muscle_group, machine_type_id, limit, offset)
