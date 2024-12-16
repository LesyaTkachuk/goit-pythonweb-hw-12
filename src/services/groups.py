from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.repository.groups import GroupRepository
from src.schemas import GroupModel, GroupResponse
from src.database.models import User
from src.conf import messages


def _handle_integrity_error(e: IntegrityError):
    if "unique_tag_user" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.GROUP_ALREADY_EXISTS,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.INTEGRITY_ERROR,
        )


class GroupService:
    def __init__(self, db: AsyncSession):
        self.repository = GroupRepository(db)

    async def create_group(self, body: GroupModel, user: User):
        try:
            return await self.repository.create_group(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def get_groups(self, skip: int, limit: int, user: User):
        return await self.repository.get_groups(skip, limit, user)

    async def get_group(self, group_id: int, user: User):
        return await self.repository.get_group_by_id(group_id, user)

    async def update_group(self, group_id: int, body: GroupModel, user: User):
        try:

            return await self.repository.update_group(group_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def remove_group(self, group_id: int, user: User):
        return await self.repository.remove_group(group_id, user)
