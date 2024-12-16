from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Group, User
from src.schemas import GroupModel, GroupResponse


class GroupRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the GroupRepository.

        Args:
            session: An AsyncSession object representing the database session.
        """
        self.db = session

    async def get_groups(self, skip: int, limit: int, user: User) -> List[Group]:
        """
        Get a list of groups owned by the user with pagination and filtering.

        Args:
            skip (int): The number of groups to skip.
            limit (int): The maximum number of groups to retrieve.
            user (User): The user object representing the user who owns the groups.

        Returns:
            List[Group]: A list of Group objects representing the filtered groups.
        """
        stmt = select(Group).filter_by(user=user).offset(skip).limit(limit)
        groups = await self.db.execute(stmt)
        return groups.scalars().all()

    async def get_group_by_id(self, group_id: int, user: User) -> Group | None:
        """
        Get a group by its ID.

        Args:
            group_id (int): The ID of the group to retrieve.
            user (User): The user object representing the user who owns the group.

        Returns:
            Group | None: The Group object representing the group with the given ID, or None if not found.
        """
        stmt = select(Group).filter_by(id=group_id, user=user)
        group = await self.db.execute(stmt)
        return group.scalar_one_or_none()

    async def create_group(self, body: GroupModel, user: User) -> Group:
        """
        Create a new group with the provided details.

        Args:
            body (GroupModel): The GroupModel object containing the group details.
            user (User): The user object representing the user who owns the group.

        Returns:
            Group: The created Group object.
        """
        group = Group(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update_group(
        self, group_id: int, body: GroupModel, user: User
    ) -> Group | None:
        """
        Update a group by its ID.

        Args:
            group_id (int): The ID of the group to update.
            body (GroupModel): The GroupModel object containing the updated group details.
            user (User): The user object representing the user who owns the group.

        Returns:
            Group | None: The updated Group object, or None if not found.
        """
        group = await self.get_group_by_id(group_id, user)
        if group:
            group.name = body.name
            await self.db.commit()
            await self.db.refresh(group)

        return group

    async def remove_group(self, group_id: int, user: User) -> Group | None:
        """
        Remove a group by its ID.

        Args:
            group_id (int): The ID of the group to remove.
            user (User): The user object representing the user who owns the group.

        Returns:
            Group | None: The removed Group object, or None if not found.
        """
        group = await self.get_group_by_id(group_id, user)
        if group:
            await self.db.delete(group)
            await self.db.commit()
        return group

    async def get_groups_by_ids(self, group_ids: List[int], user: User) -> List[Group]:
        """
        Get a list of groups by their IDs.

        Args:
            group_ids (List[int]): A list of group IDs.
            user (User): The user object representing the user who owns the groups.

        Returns:
            List[Group]: A list of Group objects representing the groups with the given IDs.
        """
        stmt = select(Group).where(Group.id.in_(group_ids), Group.user == user)
        result = await self.db.execute(stmt)
        return result.scalars().all()
