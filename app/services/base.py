"""
Base service

Defines the contract and common functionality for all services.
Services contain business logic and coordinate between endpoints and repositories.
"""

from app.core.logging import app_logger


class BaseService:
    """
    Abstract base class for all services

    This class provides a foundation for service layer components.
    Services handle business logic, validation, and orchestration between
    endpoints (controllers) and repositories (data access).

    Key responsibilities:
    - Business logic and validation
    - Coordinating multiple repository calls
    - Transaction management
    - Data transformation between layers
    - Logging business operations

    Services should be stateless and focused on a specific domain.
    """

    def __init__(self) -> None:
        """
        Initialize the service

        Override this in child classes to inject dependencies
        (repositories, other services, etc.)
        """
        self.logger = app_logger

    def _log_operation(self, operation: str, details: str | None = None) -> None:
        """
        Log a business operation

        Helper method for consistent logging across services.

        Args:
            operation: The operation being performed (e.g., "create_user")
            details: Optional details about the operation
        """
        message = f"Service operation: {operation}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    def _validate_id(self, id: int, entity_name: str = "Entity") -> None:
        """
        Validate that an ID is positive

        Args:
            id: The ID to validate
            entity_name: Name of the entity for error messages

        Raises:
            BadRequestException: If ID is invalid
        """
        if id <= 0:
            from app.core.exceptions import BadRequestException

            raise BadRequestException(
                message=f"Invalid {entity_name} ID",
                details={"id": id, "error": "ID must be a positive integer"},
            )
