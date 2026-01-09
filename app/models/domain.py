from datetime import datetime, timezone
import uuid
from typing import Optional, List

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, JSON, ARRAY, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True) # Same as Supabase Auth ID
    
    # Onboarding Answers (Goals, Equipment, Injuries, Experience Level)
    onboarding_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    
    # Physical Stats (Weight, Height, Body Fat %, Max Lifts)
    current_stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    machine_type_id: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g., "DC_BENCH"
    sensor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True) # ID of the associated sensor
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Gym location/zone ?
    zone: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    muscle_group: Mapped[str] = mapped_column(String, nullable=False) # e.g., "Pectoraux"
    
    # Logical link to machines
    machine_type_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Fallback/Alternatives (List of Exercise IDs)
    alternatives: Mapped[List[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True) # Supabase User ID
    name: Mapped[str] = mapped_column(String, nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False) # "Weight Loss", "Muscle Gain"
    status: Mapped[str] = mapped_column(String, default="active") # active, completed, archived
    
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="program", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String, nullable=False) # e.g., "Leg Day - Focus Squat"
    order_index: Mapped[int] = mapped_column(Integer, nullable=False) # 1, 2, 3...
    
    # The Planned Structure (JSON)
    # [
    #   { "exercise_id": "...", "target_sets": 3, "target_reps": 10, "rest_seconds": 90 },
    #   ...
    # ]
    exercises_plan: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    program: Mapped["Program"] = relationship("Program", back_populates="sessions")
    history_logs: Mapped[List["SessionHistory"]] = relationship("SessionHistory", back_populates="session")


class SessionHistory(Base):
    __tablename__ = "sessions_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("sessions.id"), nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    feedback_notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    session: Mapped[Optional["Session"]] = relationship("Session", back_populates="history_logs")
    sets: Mapped[List["SetHistory"]] = relationship("SetHistory", back_populates="session_history", cascade="all, delete-orphan")


class SetHistory(Base):
    __tablename__ = "sets_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_history_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions_history.id"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # User Input
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    reps_count: Mapped[int] = mapped_column(Integer, nullable=False)
    rpe: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-10

    # Sensor Data (Golden Record)
    sensor_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    session_history: Mapped["SessionHistory"] = relationship("SessionHistory", back_populates="sets")
