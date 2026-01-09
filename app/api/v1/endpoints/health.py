"""
Health check endpoints
"""

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.supabase import supabase_client
from app.schemas.health import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
# @limiter.limit("5/minute") This is for custom rate limit
async def health_check(request: Request) -> HealthCheck:
    """
    Health check endpoint

    Returns the status of the application and its dependencies
    """
    # Check Supabase connection
    supabase_status = "healthy"
    try:
        # Simple query to check connection
        supabase_client.table("health_check").select("*").limit(1).execute()
    except Exception:
        supabase_status = "unhealthy"

    return HealthCheck(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        services={"supabase": supabase_status, "api": "healthy"},
    )


@router.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }
