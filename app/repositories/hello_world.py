"""
Hello World repository

Data access layer for hello world messages.
Handles all database operations through Supabase.
"""

from app.core.exceptions import DatabaseException, NotFoundException
from app.core.logging import app_logger
from app.core.supabase import supabase_client
from app.repositories.base import BaseRepository
from app.schemas.hello_world import HelloMessage


class HelloRepository(BaseRepository[HelloMessage]):
    """
    Repository for hello world messages

    This class handles all database operations for the hello_messages table.
    It uses Supabase as the database backend.
    """

    def __init__(self) -> None:
        """
        Initialize the repository

        Sets up the table name and Supabase client connection.
        """
        super().__init__(table_name="hello_messages")
        self.client = supabase_client

    async def create(self, data: str) -> HelloMessage:
        """
        Create a new hello message in the database

        Args:
            data: The message content to store

        Returns:
            HelloMessage: The created message with ID and timestamp

        Raises:
            DatabaseException: If the insert operation fails
        """
        try:
            # Insert into Supabase
            response = self.client.table(self.table_name).insert({"message": data}).execute()

            if not response.data:
                raise DatabaseException(
                    message="Failed to insert message into database",
                    details={"table": self.table_name},
                )

            created_message = HelloMessage(**response.data[0])
            app_logger.info(f"Created hello message with ID: {created_message.id}")

            return created_message

        except DatabaseException:
            raise
        except Exception as e:
            app_logger.error(f"Unexpected error creating message: {str(e)}")
            raise DatabaseException(
                message="Failed to create message", details={"error": str(e)}
            ) from e

    async def get_all(self) -> list[HelloMessage]:
        """
        Retrieve all hello messages from the database

        Returns:
            List of HelloMessage objects, ordered by creation date (newest first)

        Raises:
            DatabaseException: If the query fails
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            messages = [HelloMessage(**item) for item in response.data]
            app_logger.debug(f"Retrieved {len(messages)} hello messages")

            return messages

        except Exception as e:
            app_logger.error(f"Error retrieving messages: {str(e)}")
            raise DatabaseException(
                message="Failed to retrieve messages", details={"error": str(e)}
            ) from e

    async def get_by_id(self, id: int) -> HelloMessage | None:
        """
        Retrieve a specific message by ID

        Args:
            id: The ID of the message to retrieve

        Returns:
            HelloMessage if found, None otherwise

        Raises:
            DatabaseException: If the query fails
        """
        try:
            response = (
                self.client.table(self.table_name).select("*").eq("id", id).maybe_single().execute()
            )

            if not response.data:
                return None

            return HelloMessage(**response.data)

        except Exception as e:
            app_logger.error(f"Error retrieving message {id}: {str(e)}")
            raise DatabaseException(
                message=f"Failed to retrieve message {id}", details={"error": str(e)}
            ) from e

    async def update(self, id: int, data: str) -> HelloMessage:
        """
        Update a message by ID

        Args:
            id: The ID of the message to update
            data: The new message content

        Returns:
            The updated HelloMessage

        Raises:
            NotFoundException: If message doesn't exist
            DatabaseException: If the update operation fails
        """
        try:
            # Check if message exists
            existing = await self.get_by_id(id)
            if not existing:
                raise NotFoundException(
                    message=f"Message with ID {id} not found", details={"message_id": id}
                )

            # Update the message
            response = (
                self.client.table(self.table_name).update({"message": data}).eq("id", id).execute()
            )

            if not response.data:
                raise DatabaseException(
                    message=f"Failed to update message {id}", details={"message_id": id}
                )

            updated_message = HelloMessage(**response.data[0])
            app_logger.info(f"Updated hello message with ID: {id}")

            return updated_message

        except (NotFoundException, DatabaseException):
            raise
        except Exception as e:
            app_logger.error(f"Error updating message {id}: {str(e)}")
            raise DatabaseException(
                message=f"Failed to update message {id}", details={"error": str(e)}
            ) from e

    async def delete(self, id: int) -> bool:
        """
        Delete a message by ID

        Args:
            id: The ID of the message to delete

        Returns:
            True if deletion was successful

        Raises:
            NotFoundException: If message doesn't exist
            DatabaseException: If the delete operation fails
        """
        try:
            # Check if message exists
            existing = await self.get_by_id(id)
            if not existing:
                raise NotFoundException(
                    message=f"Message with ID {id} not found", details={"message_id": id}
                )

            # Delete the message
            self.client.table(self.table_name).delete().eq("id", id).execute()

            app_logger.info(f"Deleted hello message with ID: {id}")
            return True

        except (NotFoundException, DatabaseException):
            raise
        except Exception as e:
            app_logger.error(f"Error deleting message {id}: {str(e)}")
            raise DatabaseException(
                message=f"Failed to delete message {id}", details={"error": str(e)}
            ) from e
