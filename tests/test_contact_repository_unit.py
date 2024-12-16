import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from src.database.models import User, Group, Contact
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate, GroupModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id="u-1", username="testuser")


@pytest.fixture
def contact(user):
    return Contact(
        id="c-1",
        name="test name",
        surname="test surname",
        email="test@test.com",
        phone_number="+38099238238",
        birthday="2000-01-01",
        user_id=user.id,
        user=user,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(
        skip=0, limit=10, query="unexisting", user=user
    )

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].name == "test name"
    assert contacts[0].email == "test@test.com"


@pytest.mark.asyncio
async def test_get_contacts_with_query(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(
        skip=0, limit=10, query="", user=user
    )

    # Assertions
    assert len(contacts) == 0


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user, contact):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id="c-1", user=user)

    # Assertions
    assert contact is not None
    assert contact.id == "c-1"
    assert contact.name == "test name"
    assert contact.email == "test@test.com"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        name="new contact",
        email="new-test@test.com",
        surname="new surname",
        phone_number="+38099238238",
        birthday="2000-01-01",
        groups=[1],
        user=user,
    )
    groups = [Group(id="g-1", name="test group", user=user)]
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id="c-2",
        name="new contact",
        surname="new surname",
        phone_number="+38099238238",
        birthday="2000-01-01",
        email="new-test@test.com",
        groups=groups,
        user_id=user.id,
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.create_contact(
        body=contact_data, groups=groups, user=user
    )

    # Assertions
    assert isinstance(result, Contact)
    assert result.name == "new contact"
    assert result.email == "new-test@test.com"
    assert len(result.groups) == 1


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user, contact):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id="c-1", user=user)

    # Assertions
    assert result is not None
    assert result.name == "test name"
    mock_session.delete.assert_awaited_once_with(contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user, contact):
    # Setup
    note_data = ContactUpdate(
        name="updated name",
        surname="updated surname",
        email="updated.test@test.com",
        phone_number="+38099238238",
        birthday="2000-01-01",
        groups=[],
        is_active=True,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id="c-1", body=note_data, groups=[], user=user
    )

    # Assertions
    assert result is not None
    assert result.name == "updated name"
    assert result.surname == "updated surname"
    assert result.is_active is True
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)


@pytest.mark.asyncio
async def update_contact_is_active(contact_repository, mock_session, user):
    # Setup
    is_active_updated = ContactUpdate(is_active=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact_is_active(
        contact_id="c-1", body=is_active_updated, user=user
    )

    # Assertions
    assert result is not None
    assert result.is_active is False
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)


@pytest.mark.asyncio
async def test_get_contacts_by_birthday(
    contact_repository, mock_session, user, contact
):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)
    # Call method
    contacts = await contact_repository.get_contacts_by_birthday(
        from_date=date(2000, 1, 1), to_date=date(2000, 2, 1), user=user
    )

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].name == "test name"
    assert contacts[0].birthday == "2000-01-01"
