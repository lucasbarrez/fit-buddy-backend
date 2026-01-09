"""
API v1 router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, hello_world, profile

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(hello_world.router, prefix="/hello", tags=["hello-world"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
