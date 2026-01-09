from typing import Any
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user_db import get_db
from app.api.dependencies import get_current_user

from app.schemas.common import SuccessResponse
from app.schemas.program import ProgramRead, ProgramGenerateResponse
from app.repositories.program import ProgramRepository
from app.repositories.profile import ProfileRepository
from app.repositories.dictionary import DictionaryRepository
from app.services.program import ProgramService
from app.services.knowledge import KnowledgeService
from app.services.rag import KnowledgeRetriever
from app.services.program_generator import ProgramGenerator

router = APIRouter()


@router.post("/generate", response_model=SuccessResponse[ProgramGenerateResponse])
async def generate_program(
    method: str = "template",
    current_user: dict = Depends(get_current_user),
    service: ProgramService = Depends(get_program_service),
) -> Any:
    """
    Generate a new workout program based on user's existing profile.
    Archives any currently active program.
    Method can be 'template' (default) or 'smart' (AI RAG).
    """
    user_id = current_user["id"]
    program = await service.generate_program(user_id, method=method)
    return SuccessResponse(
        data=ProgramGenerateResponse(
            program=program,
            message=f"New program generated successfully ({method} mode)."
        ),
        message="Program generated"
    )

async def get_program_service(session: AsyncSession = Depends(get_db)) -> ProgramService:
    prog_repo = ProgramRepository(session)
    prof_repo = ProfileRepository(session)
    dict_repo = DictionaryRepository(session)
    
    # RAG Dependencies
    knowledge_service = KnowledgeService()
    retriever = KnowledgeRetriever(session)
    generator = ProgramGenerator(knowledge_service, retriever)
    
    return ProgramService(prog_repo, prof_repo, dict_repo, generator)


@router.get("/current", response_model=SuccessResponse[ProgramRead])
async def get_current_program(
    current_user: dict = Depends(get_current_user),
    service: ProgramService = Depends(get_program_service),
) -> Any:
    """
    Get the currently active program.
    """
    user_id = current_user["id"]
    program = await service.get_current_program(user_id)
    return SuccessResponse(data=program)
