"""
Common response schemas
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Error detail schema"""

    field: str | None = None
    message: str
    type: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    message: str
    status_code: int
    details: dict[str, Any] | None = None
    errors: list[ErrorDetail] | None = None


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success response"""

    success: bool = True
    message: str = "Success"
    data: DataT | None = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    page: int = Field(ge=1, description="Current page number")
    per_page: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total items")
    total_pages: int = Field(ge=0, description="Total pages")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated response"""

    success: bool = True
    message: str = "Success"
    data: list[DataT]
    meta: PaginationMeta
