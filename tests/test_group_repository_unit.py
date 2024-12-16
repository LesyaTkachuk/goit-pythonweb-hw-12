import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Group, User
from src.repository.groups import GroupRepository
from src.schemas import GroupModel, GroupResponse


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def group_repository(mock_session):
    return GroupRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser", email="testemail")


@pytest.fixture
def group(user: User):
    return Group(id=1, name="test group", user_id=user.id, user=user)


@pytest.mark.asyncio
async def test_get_groups(group_repository, mock_session, user, group):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [group]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    groups = await group_repository.get_groups(skip=0, limit=10, user=user)

    # Assertions
    assert len(groups) == 1
    assert groups[0].name == "test group"
    assert groups[0].name != "test group 1"


@pytest.mark.asyncio
async def test_get_group_by_id(group_repository, mock_session, user, group):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = group
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    group = await group_repository.get_group_by_id(group_id=1, user=user)

    # Assertions
    assert group is not None
    assert group.id == 1
    assert group.name == "test group"


@pytest.mark.asyncio
async def test_create_group(group_repository, mock_session, user):
    # Setup
    group_data = GroupModel(name="new group")

    # Call method
    result = await group_repository.create_group(body=group_data, user=user)

    # Assertions
    assert isinstance(result, Group)
    assert result.name == "new group"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_group(group_repository, mock_session, user):
    # Setup
    group_data = GroupModel(name="updated group")
    existing_group = Group(id=1, name="old tag", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_group
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await group_repository.update_group(group_id=1, body=group_data, user=user)

    # Assertions
    assert result is not None
    assert result.name == "updated group"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_group)


@pytest.mark.asyncio
async def test_remove_group(group_repository, mock_session, user, group):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = group
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await group_repository.remove_group(group_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.name == "test group"
    mock_session.delete.assert_awaited_once_with(group)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_groups_by_ids(group_repository, mock_session, user, group):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        group,
        Group(id=2, name="test group 2", user=user),
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await group_repository.get_groups_by_ids(group_ids=[1, 2], user=user)

    # Assertions
    assert result is not None
    assert result[0].name == "test group"
    assert result[1].name == "test group 2"
    mock_session.execute.assert_awaited_once()
