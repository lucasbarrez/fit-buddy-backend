"""
API v1 router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    hello_world,
    health,
    auth,
    profile,
    dictionary,
    program,
    session
)

api_router = APIRouter()

api_router.include_router(hello_world.router, prefix="/hello", tags=["Hello World"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(dictionary.router, prefix="/dictionary", tags=["Dictionary"])
api_router.include_router(program.router, prefix="/program", tags=["Program"])
api_router.include_router(session.router, prefix="/session", tags=["Session Tracking"])
