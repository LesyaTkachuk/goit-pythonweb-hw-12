from typing import List


from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.conf import messages
from src.database.models import User
from src.schemas import GroupModel, GroupResponse
from src.services.groups import GroupService
from src.services.auth import get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupResponse])
async def read_groups(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of groups for the authenticated user.

    Args:
        skip (int): The number of groups to skip.
        limit (int): The maximum number of groups to retrieve.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        List[GroupResponse]: A list of GroupResponse objects representing the groups.
    """
    group_service = GroupService(db)
    groups = await group_service.get_groups(skip, limit, user)
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
async def read_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a group by its ID.

    Args:
        group_id (int): The ID of the group to retrieve.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        Group | None: The Group object, or None if not found.
    """
    group_service = GroupService(db)
    group = await group_service.get_group(group_id, user)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.GROUP_NOT_FOUND
        )

    return group


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    body: GroupModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new group.

    Args:
        body (GroupModel): The GroupModel object representing the group to create.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        GroupResponse: The GroupResponse object representing the created group.
    """
    group_service = GroupService(db)
    return await group_service.create_group(body, user)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    body: GroupModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update a group by its ID.

    Args:
        group_id (int): The ID of the group to update.
        body (GroupModel): The GroupModel object representing the updated group details.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
         Group | None: The updated Group object, or None if not found.
    """
    group_service = GroupService(db)
    group = await group_service.update_group(group_id, body, user)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.GROUP_NOT_FOUND
        )
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Remove a group by its ID.

    Args:
        group_id (int): The ID of the group to remove.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        Group | None: The removed Group object, or None if not found.
    """
    group_service = GroupService(db)
    return await group_service.remove_group(group_id, user)


# @router.delete("/{group_id}", response_model=GroupResponse)
# async def remove_group(group_id: int, db: AsyncSession = Depends(get_db)):
#     group_service = GroupService(db)
#     group = await group_service.remove_group(group_id)
#     if group is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
#         )
#     return group
