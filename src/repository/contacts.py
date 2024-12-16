from typing import List, Optional
from datetime import datetime, timedelta, date

from sqlalchemy import and_, or_, select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact, Group, User
from src.schemas import ContactModel, ContactUpdate, ContactIsActiveUpdate


class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactRepository.

        Args:
            session: An AsyncSession object representing the database session.
        """
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, query: str | None, user: User
    ) -> List[Contact]:
        """
        Get a list of contacts owned by the user with pagination and filtering.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to retrieve.
            query (str | None): The search query for filtering contacts by name, surname, or email.
            user (User): The user object representing the user who owns the contacts.

        Returns:
            List[Contact]: A list of Contact objects representing the filtered contacts.
        """
        # selectinload - to get groups connected with this contact
        # skip and limit - pagination realization
        query = query.lower() if query is not None else ""
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .options(selectinload(Contact.groups))
            .filter(
                (Contact.name.ilike(f"%{query}%"))
                | (Contact.surname.ilike(f"%{query}%"))
                | (Contact.email.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Get a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user object representing the user who owns the contact.

        Returns:
            Contact | None: The Contact object representing the contact with the given ID, or None if not found.
        """
        stmt = (
            select(Contact)
            .options(selectinload(Contact.groups))
            .filter_by(id=contact_id, user=user)
        )
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(
        self, body: ContactModel, groups: List[Group], user: User
    ) -> Contact:
        """
        Create a new contact with the provided details.

        Args:
            body (ContactModel): The ContactModel object containing the contact details.
            groups (List[Group]): A list of Group objects representing the contact's groups.
            user (User): The user object representing the user who owns the contact.

        Returns:
            Contact: The created Contact object.
        """
        contact = Contact(
            **body.model_dump(exclude={"groups"}, exclude_unset=True),
            groups=groups,
            user=user,
        )
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user object representing the user who owns the contact.

        Returns:
            Contact | None: The deleted Contact object, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, groups: List[Group], user: User
    ) -> Contact | None:
        """
        Update a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The ContactUpdate object containing the updated contact details.
            groups (List[Group]): A list of Group objects representing the contact's groups.
            user (User): The user object representing the user who owns the contact.

        Returns:
            Contact | None: The updated Contact object, or None if not found.
        """
        # exclude_unset - exclude the field if it's None
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(
                exclude_unset=True, exclude={"groups"}
            ).items():
                setattr(contact, key, value)

            if groups is not None:
                contact.groups = groups

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def update_contact_is_active(
        self, contact_id: int, body: ContactIsActiveUpdate, user: User
    ) -> Contact | None:
        """
        Update the is_active field of a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactIsActiveUpdate): The ContactIsActiveUpdate object containing the updated is_active value.
            user (User): The user object representing the user who owns the contact.

        Returns:
            Contact | None: The updated Contact object, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            contact.is_active = body.is_active
            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_contacts_by_birthday(
        self, from_date: date | None, to_date: date | None, user: User
    ) -> List[Contact]:
        """
        Get a list of contacts whose birthdays fall within the specified date range.

        Args:
            from_date (date | None): The start date of the date range.
            to_date (date | None): The end date of the date range.
            user (User): The user object representing the user who owns the contacts.

        Returns:
            List[Contact]: A list of Contact objects whose birthdays fall within the specified date range.
        """
        # Default range: next 7 days
        from_date = from_date or datetime.now().date()
        to_date = to_date or (from_date + timedelta(days=7))

        # extract month and day for the given range
        from_month, from_day = from_date.month, from_date.day
        to_month, to_day = to_date.month, to_date.day
        print("from_month", from_month, "from_day", from_day)
        print("to_month", to_month, "to_day", to_day)
        # construct the SQL query
        if from_month == to_month:  # Same month case
            stmt = (
                select(Contact)
                .filter_by(user=user)
                .options(selectinload(Contact.groups))
                .filter(
                    extract("month", Contact.birthday) == from_month,
                    extract("day", Contact.birthday) >= from_day,
                    extract("day", Contact.birthday) < to_day,
                )
            )
        else:  # cross-month case (e.g., December -> January)
            stmt = (
                select(Contact)
                .filter_by(user=user)
                .options(selectinload(Contact.groups))
                .filter(
                    or_(
                        # remaining days in the starting month
                        and_(
                            extract("month", Contact.birthday) == from_month,
                            extract("day", Contact.birthday) >= from_day,
                        ),
                        # days in the next month
                        and_(
                            extract("month", Contact.birthday) == to_month,
                            extract("day", Contact.birthday) < to_day,
                        ),
                    )
                )
            )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
