"""
Base repository

Defines the contract that all repositories must follow.
Provides common database operation interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base class for all repositories

    This class defines the standard interface that all repositories must implement.
    It ensures consistency across data access layers and makes it easy to swap
    implementations or add new repositories.

    Attributes:
        table_name: Name of the database table this repository manages

    Type Parameters:
        T: The model type this repository works with (e.g., HelloMessage)
    """

    def __init__(self, table_name: str) -> None:
        """
        Initialize the repository

        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        """
        Retrieve a single record by its ID

        Args:
            id: The unique identifier of the record

        Returns:
            The record if found, None otherwise

        Raises:
            DatabaseException: If the query fails
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[T]:
        """
        Retrieve all records from the table

        Returns:
            List of all records

        Raises:
            DatabaseException: If the query fails
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: Any) -> T:
        """
        Create a new record in the database

        Args:
            data: The data to create (can be dict, model, or primitive)

        Returns:
            The created record with generated fields (ID, timestamps, etc.)

        Raises:
            DatabaseException: If the insert fails
            ValidationException: If data validation fails
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: int, data: Any) -> T:
        """
        Update an existing record

        Args:
            id: The ID of the record to update
            data: The data to update (can be dict, model, or partial data)

        Returns:
            The updated record

        Raises:
            NotFoundException: If the record doesn't exist
            DatabaseException: If the update fails
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        Delete a record by its ID

        Args:
            id: The ID of the record to delete

        Returns:
            True if deletion was successful

        Raises:
            NotFoundException: If the record doesn't exist
            DatabaseException: If the delete fails
        """
        raise NotImplementedError

    # Optional common methods (non-abstract) that can be overridden

    async def exists(self, id: int) -> bool:
        """
        Check if a record exists by ID

        Default implementation uses get_by_id.
        Can be overridden for better performance.

        Args:
            id: The ID to check

        Returns:
            True if record exists, False otherwise
        """
        result = await self.get_by_id(id)
        return result is not None

    async def count(self) -> int:
        """
        Count total records in the table

        Default implementation gets all records and counts them.
        Should be overridden with a proper COUNT query for better performance.

        Returns:
            Total number of records
        """
        records = await self.get_all()
        return len(records)
