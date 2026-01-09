from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Program, Session, SessionHistory


class ProgramRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_program(self, user_id: UUID) -> Optional[Program]:
        query = (
            select(Program)
            .where(Program.user_id == user_id, Program.status == "active")
            .options(selectinload(Program.sessions))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_program(self, program: Program, sessions: List[Session]) -> Program:
        self.session.add(program)
        await self.session.flush() # Generate Program ID
        
        for s in sessions:
            s.program_id = program.id
            self.session.add(s)
            
        await self.session.commit()
        await self.session.refresh(program)
        # Re-fetch with sessions to ensure relationships are loaded
        return await self.get_active_program(program.user_id)
        
    async def archive_current_programs(self, user_id: UUID) -> None:
        stmt = (
            update(Program)
            .where(Program.user_id == user_id, Program.status == "active")
            .values(status="archived", end_date=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_program_by_id(self, program_id: UUID) -> Optional[Program]:
        query = (
            select(Program)
            .where(Program.id == program_id)
            .options(selectinload(Program.sessions))
        )
        result = await self.session.execute(query)
        return result.scalars().first()
