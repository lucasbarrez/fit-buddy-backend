"""
Hello World service

Business logic layer for hello world messages.
Coordinates between endpoints and repositories.
"""

from app.core.logging import app_logger
from app.repositories.hello_world import HelloRepository
from app.schemas.hello_world import HelloRequest, HelloResponse
from app.services.base import BaseService


class HelloService(BaseService):
    """
    Service for hello world message operations

    This service handles the business logic for hello world messages,
    coordinating between the API endpoints and the database repository.
    """

    def __init__(self) -> None:
        """
        Initialize the service

        Sets up the repository dependency.
        """
        super().__init__()
        self.repository = HelloRepository()

    async def create_hello_message(self, request: HelloRequest) -> HelloResponse:
        """
        Create a new hello message

        Args:
            request: The request containing the message to create

        Returns:
            HelloResponse: The created message with ID and timestamp

        Raises:
            DatabaseException: If the database operation fails
        """
        app_logger.info(f"Creating hello message: {request.message[:50]}...")

        # Repository handles validation and database insertion
        message = await self.repository.create(request.message)

        # Convert to response format
        return HelloResponse(
            id=message.id or 0,
            message=message.message,
            created_at=message.created_at.isoformat() if message.created_at else "",
        )

    async def get_all_messages(self) -> list[HelloResponse]:
        """
        Retrieve all hello messages

        Returns:
            List of HelloResponse objects, ordered by creation date

        Raises:
            DatabaseException: If the database query fails
        """
        app_logger.debug("Retrieving all hello messages")

        # Get all messages from repository
        messages = await self.repository.get_all()

        # Convert to response format
        return [
            HelloResponse(
                id=msg.id or 0,
                message=msg.message,
                created_at=msg.created_at.isoformat() if msg.created_at else "",
            )
            for msg in messages
        ]

    async def get_message_by_id(self, message_id: int) -> HelloResponse:
        """
        Retrieve a specific message by ID

        Args:
            message_id: The ID of the message to retrieve

        Returns:
            HelloResponse: The message data

        Raises:
            NotFoundException: If the message doesn't exist
            DatabaseException: If the database query fails
        """
        app_logger.debug(f"Retrieving hello message with ID: {message_id}")

        message = await self.repository.get_by_id(message_id)

        if not message:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(
                message=f"Message with ID {message_id} not found",
                details={"message_id": message_id},
            )

        return HelloResponse(
            id=message.id or 0,
            message=message.message,
            created_at=message.created_at.isoformat() if message.created_at else "",
        )

    async def delete_message(self, message_id: int) -> bool:
        """
        Delete a message by ID

        Args:
            message_id: The ID of the message to delete

        Returns:
            True if deletion was successful

        Raises:
            NotFoundException: If the message doesn't exist
            DatabaseException: If the delete operation fails
        """
        app_logger.info(f"Deleting hello message with ID: {message_id}")

        return await self.repository.delete(message_id)
