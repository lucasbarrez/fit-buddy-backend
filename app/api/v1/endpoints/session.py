from typing import Any, List
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.user_db import get_db
from app.api.dependencies import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.session import (
    AvailabilityResponse, 
    SessionStartRequest, SessionStartResponse,
    SetLogRequest, SetLogResponse,
    SessionStopRequest, SessionStopResponse,
    SessionDetailResponse, ExerciseStatsResponse
)
from app.models.domain import SessionHistory, SetHistory
from app.repositories.dictionary import DictionaryRepository
from app.repositories.session import SessionRepository
from app.services.iot import IoTService
from app.services.rag import KnowledgeRetriever
from app.services.knowledge import KnowledgeService
from app.services.adaptation import AdaptationService

router = APIRouter()

# --- Dependencies ---

async def get_adaptation_service(session: AsyncSession = Depends(get_db)) -> AdaptationService:
    iot = IoTService()
    dict_repo = DictionaryRepository(session)
    retriever = KnowledgeRetriever(session)
    session_repo = SessionRepository(session)
    return AdaptationService(iot, dict_repo, retriever, session_repo)

async def get_session_repo(session: AsyncSession = Depends(get_db)) -> SessionRepository:
    return SessionRepository(session)

# --- Routes ---

@router.get("/check-availability/{exercise_id}", response_model=SuccessResponse[AvailabilityResponse])
async def check_availability(
    exercise_id: UUID,
    service: AdaptationService = Depends(get_adaptation_service),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Real-time check using IoT Mock.
    Returns wait time and alternatives if busy.
    """
    result = await service.check_exercise_availability(exercise_id, user_profile=current_user)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
        
    return SuccessResponse(data=AvailabilityResponse(**result))

@router.post("/start", response_model=SuccessResponse[SessionStartResponse])
async def start_session(
    data: SessionStartRequest,
    repo: SessionRepository = Depends(get_session_repo),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Start a new workout session.
    """
    new_history = await repo.create_history(
        user_id=current_user["id"],
        session_id=data.session_id
    )
    
    return SuccessResponse(
        data=SessionStartResponse(
            session_history_id=new_history.id,
            started_at=new_history.started_at,
            message="Session started! Go crush it!"
        )
    )

from app.services.sensor import SensorService

@router.post("/set", response_model=SuccessResponse[SetLogResponse])
async def log_set(
    data: SetLogRequest,
    repo: SessionRepository = Depends(get_session_repo),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Log a completed set with optional Sensor Sync.
    """
    history = await repo.get_history(data.session_history_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session history not found")
        
    if str(history.user_id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Not your session")
    
    # --- Precision Tracking Logic ---
    sensor_service = SensorService()
    sensor_data = {}
    
    # If client provides machine_id (QR Code), use it directly.
    # Otherwise, for demo purposes, we can simulate that the user is on the "correct" machine
    # if we want to show off the feature.
    machine_id = data.machine_id
    
    if machine_id:
        # Fetch "Golden Record" from Sensor API using precise timestamps
        # Be careful: if client didn't send times, we fallback to now() which might miss the window.
        t_end = data.end_time or datetime.now(timezone.utc)
        t_start = data.start_time or t_end
        
        sensor_data = await sensor_service.get_sensor_snapshot(
            machine_id, 
            start_time=t_start,
            end_time=t_end
        )
        
    new_set = await repo.add_set(
        session_history_id=data.session_history_id,
        exercise_id=data.exercise_id,
        weight=data.weight_kg,
        reps=data.reps_count,
        rpe=data.rpe,
        machine_id=machine_id,
        sensor_data=sensor_data,
        start_time=data.start_time,
        end_time=data.end_time
    )
    
    msg = "Set logged."
    if sensor_data:
        msg = f"Set logged + Synced with {machine_id} (Power: {sensor_data['metrics']['avg_power_watts']}W)"
    
    return SuccessResponse(
        data=SetLogResponse(
            set_history_id=new_set.id,
            message=msg
        )
    )

@router.post("/stop", response_model=SuccessResponse[SessionStopResponse])
async def stop_session(
    data: SessionStopRequest,
    repo: SessionRepository = Depends(get_session_repo),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Stop and finalize the session.
    """
    history = await repo.get_history(data.session_history_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session history not found")
        
    if str(history.user_id) != str(current_user["id"]):
         raise HTTPException(status_code=403, detail="Not your session")
         
    updated_history = await repo.finish_session(history, data.feedback_notes)
    
    duration = 0.0
    if updated_history.started_at and updated_history.finished_at:
        duration = (updated_history.finished_at - updated_history.started_at).total_seconds() / 60.0
    
    return SuccessResponse(
        data=SessionStopResponse(
            session_history_id=updated_history.id,
            finished_at=updated_history.finished_at,
            duration_minutes=duration,
            total_xp=updated_history.total_xp,
            message="Session complete! Great job."
        )
    )

@router.get("/history/{session_history_id}", response_model=SuccessResponse[SessionDetailResponse])
async def get_session_details(
    session_history_id: UUID,
    repo: SessionRepository = Depends(get_session_repo),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get full details of a session (including all sets).
    """
    history = await repo.get_full_session(session_history_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if str(history.user_id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Not your session")
        
    return SuccessResponse(data=SessionDetailResponse.model_validate(history))

@router.get("/stats/{exercise_id}", response_model=SuccessResponse[List[ExerciseStatsResponse]])
async def get_exercise_stats(
    exercise_id: UUID,
    repo: SessionRepository = Depends(get_session_repo),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get progression history for an exercise.
    """
    stats = await repo.get_exercise_history(current_user["id"], exercise_id)
    return SuccessResponse(data=[ExerciseStatsResponse(**s) for s in stats])
