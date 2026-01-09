"""
Hello World endpoints - Example implementation
"""

from fastapi import APIRouter, Depends, Request, status

from app.middleware.rate_limit import limiter
from app.schemas.common import SuccessResponse
from app.schemas.hello_world import HelloRequest, HelloResponse
from app.services.hello_world import HelloService

router = APIRouter()


def get_hello_service() -> HelloService:
    """Dependency to get hello service"""
    return HelloService()


@router.post(
    "/",
    response_model=SuccessResponse[HelloResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a hello message",
    description="Create a new hello message in the database",
)
@limiter.limit("10/minute")
async def create_hello_message(
    request: Request,
    hello_request: HelloRequest,
    service: HelloService = Depends(get_hello_service),
) -> SuccessResponse[HelloResponse]:
    """Create a hello message"""
    data = await service.create_hello_message(hello_request)
    return SuccessResponse(message="Message created successfully", data=data)


@router.get(
    "/",
    response_model=SuccessResponse[list[HelloResponse]],
    summary="Get all hello messages",
    description="Retrieve all hello messages from the database",
)
async def get_all_messages(
    service: HelloService = Depends(get_hello_service),
) -> SuccessResponse[list[HelloResponse]]:
    """Get all hello messages"""
    data = await service.get_all_messages()
    return SuccessResponse(message="Messages retrieved successfully", data=data)
