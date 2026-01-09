from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user_db import get_db

from app.schemas.common import SuccessResponse
from app.schemas.dictionary import MachineRead, ExerciseRead
from app.repositories.dictionary import DictionaryRepository
from app.services.dictionary import DictionaryService

router = APIRouter()

async def get_dictionary_service(session: AsyncSession = Depends(get_db)) -> DictionaryService:
    repo = DictionaryRepository(session)
    return DictionaryService(repo)


@router.get("/machines", response_model=SuccessResponse[List[MachineRead]])
async def list_machines(
    service: DictionaryService = Depends(get_dictionary_service),
) -> Any:
    """
    List all available machines/equipment.
    """
    machines = await service.list_machines()
    return SuccessResponse(data=machines)


@router.get("/exercises", response_model=SuccessResponse[List[ExerciseRead]])
async def list_exercises(
    muscle_group: Optional[str] = Query(None, description="Filter by muscle group"),
    machine_type: Optional[str] = Query(None, description="Filter by machine type ID"),
    limit: int = 100,
    offset: int = 0,
    service: DictionaryService = Depends(get_dictionary_service),
) -> Any:
    """
    List exercises with optional filtering.
    """
    exercises = await service.list_exercises(
        muscle_group=muscle_group,
        machine_type_id=machine_type,
        limit=limit,
        offset=offset
    )
    return SuccessResponse(data=exercises)
