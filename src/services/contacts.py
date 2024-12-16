from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.repository.groups import GroupRepository
from src.schemas import ContactModel, ContactUpdate, ContactIsActiveUpdate
from src.database.models import User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)
        self.group_repository = GroupRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        groups = await self.group_repository.get_groups_by_ids(body.groups, user)
        return await self.contact_repository.create_contact(body, groups, user)

    async def get_contacts(self, skip: int, limit: int, query: str | None, user: User):
        return await self.contact_repository.get_contacts(skip, limit, query, user)

    async def get_contacts_by_birthday(
        self,
        from_date: date | None,
        to_date: date | None,
        user: User,
    ):
        return await self.contact_repository.get_contacts_by_birthday(
            from_date, to_date, user
        )

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        groups = await self.group_repository.get_groups_by_ids(body.groups, user)
        return await self.contact_repository.update_contact(
            contact_id, body, groups, user
        )

    async def update_contact_is_active(
        self, contact_id: int, body: ContactIsActiveUpdate, user: User
    ):
        return await self.contact_repository.update_contact_is_active(
            contact_id, body, user
        )

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)
