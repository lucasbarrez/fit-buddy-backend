"""
Health check schema
"""

from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    version: str
    environment: str
    services: dict[str, str]
