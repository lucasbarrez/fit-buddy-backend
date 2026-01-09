from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Machine, Exercise


class DictionaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_machines(self) -> List[Machine]:
        query = select(Machine).order_by(Machine.name)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_exercises(
        self, 
        muscle_group: Optional[str] = None, 
        machine_type_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Exercise]:
        query = select(Exercise)
        
        if muscle_group:
            query = query.where(Exercise.muscle_group == muscle_group)
        if machine_type_id:
            query = query.where(Exercise.machine_type_id == machine_type_id)
            
        query = query.order_by(Exercise.name).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
