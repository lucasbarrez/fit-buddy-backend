from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import SessionHistory, SetHistory

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_history(self, user_id: UUID, session_id: UUID) -> SessionHistory:
        """
        Start a new workout session history.
        """
        new_history = SessionHistory(
            user_id=user_id,
            session_id=session_id,
            started_at=datetime.now(timezone.utc),
            total_xp=0
        )
        self.session.add(new_history)
        await self.session.commit()
        await self.session.refresh(new_history)
        return new_history

    async def get_history(self, history_id: UUID) -> Optional[SessionHistory]:
        """
        Get session history by ID.
        """
        stmt = select(SessionHistory).where(SessionHistory.id == history_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_set(self, 
        session_history_id: UUID, 
        exercise_id: UUID, 
        weight: float, 
        reps: int, 
        rpe: Optional[int],
        machine_id: Optional[str] = None,
        sensor_data: Optional[dict] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> SetHistory:
        """
        Log a completed set.
        """
        # Default to "now" if not provided, allowing for quick logs
        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            # Default to 1 min duration if missing, just for data consistency
            start_time = end_time 
        
        new_set = SetHistory(
            session_history_id=session_history_id,
            exercise_id=exercise_id,
            weight_kg=weight,
            reps_count=reps,
            rpe=rpe,
            machine_id=machine_id,
            sensor_snapshot=sensor_data,
            start_time=start_time,
            end_time=end_time
        )
        self.session.add(new_set)
        await self.session.commit()
        await self.session.refresh(new_set)
        return new_set

    async def finish_session(self, history: SessionHistory, notes: Optional[str]) -> SessionHistory:
        """
        Stop the session and calculate summary stats.
        """
        history.finished_at = datetime.now(timezone.utc)
        history.feedback_notes = notes
        
        # Calculate Stats (XP, Duration)
        duration_min = 0
        if history.started_at:
            delta = history.finished_at - history.started_at
            duration_min = delta.total_seconds() / 60.0
            
        # XP Rule: 10 XP per minute + bonus for completion
        history.total_xp = int(duration_min * 10) + 50
        
        await self.session.commit()
        return history

    async def get_recent_best_set(self, user_id: UUID, exercise_id: UUID) -> Optional[dict]:
        """
        Fetch the best performance (max weight) for a specific exercise by this user.
        """
        # Join SetHistory -> SessionHistory to filter by user
        stmt = (
            select(SetHistory.weight_kg, SetHistory.reps_count, SetHistory.rpe, SessionHistory.started_at)
            .join(SessionHistory, SetHistory.session_history_id == SessionHistory.id)
            .where(SessionHistory.user_id == user_id)
            .where(SetHistory.exercise_id == exercise_id)
            .order_by(SetHistory.weight_kg.desc()) # Max Weight
            .limit(1)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row:
             return {
                 "weight_kg": row.weight_kg,
                 "reps": row.reps_count,
                 "rpe": row.rpe,
                 "date": row.started_at.strftime("%Y-%m-%d")
             }
        return None

    async def get_full_session(self, history_id: UUID) -> Optional[SessionHistory]:
        """
        Get session history with all sets loaded.
        """
        from sqlalchemy.orm import selectinload
        stmt = (
            select(SessionHistory)
            .where(SessionHistory.id == history_id)
            .options(selectinload(SessionHistory.sets))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_exercise_history(self, user_id: UUID, exercise_id: UUID, limit: int = 20) -> list[dict]:
        """
        Get recent history for a specific exercise to track progression.
        """
        stmt = (
            select(SetHistory, SessionHistory.started_at)
            .join(SessionHistory, SetHistory.session_history_id == SessionHistory.id)
            .where(SessionHistory.user_id == user_id)
            .where(SetHistory.exercise_id == exercise_id)
            .order_by(SessionHistory.started_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        
        history = []
        for set_row, date in result:
            # Epley Formula for 1RM
            e1rm = set_row.weight_kg * (1 + set_row.reps_count / 30.0)
            history.append({
                "date": date,
                "weight_kg": set_row.weight_kg,
                "reps": set_row.reps_count,
                "one_rep_max_est": round(e1rm, 1)
            })
        return history
