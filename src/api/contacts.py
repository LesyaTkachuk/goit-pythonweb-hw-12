from typing import List
from datetime import date

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.conf import messages
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactIsActiveUpdate,
    ContactResponse,
)
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 20,
    query: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get a list of contacts owned by the user with pagination and filtering.

    Args:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to retrieve.
        query (str | None): The search query for filtering contacts by name, surname, or email.
        db (AsyncSession): The database session to be used to get the contacts.
        user (User): The user object representing the user who owns the contacts.

    Returns:
        List[Contact]: A list of Contact objects representing the filtered contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, query, user)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact for the user.

    Args:
        body (ContactModel): The ContactModel object representing the contact to create.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The ContactResponse object representing the created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.get("/birthday", response_model=List[ContactResponse])
async def filter_contacts_by_birthday(
    from_date: date | None = None,
    to_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get a list of contacts whose birthdays fall within the specified date range.

    Args:
        from_date (date | None): The start date of the date range.
        to_date (date | None): The end date of the date range.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        List[ContactResponse]: A list of ContactResponse objects representing the filtered contacts.

    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_by_birthday(from_date, to_date, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The ContactResponse object representing the retrieved contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactUpdate): The ContactUpdate object representing the updated contact details.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The ContactResponse object representing the updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact_is_active(
    contact_id: int,
    body: ContactIsActiveUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update the is_active field of a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactIsActiveUpdate): The ContactIsActiveUpdate object containing the updated is_active value.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The ContactResponse object representing the updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact_is_active(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Remove a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to remove.
        db (AsyncSession): The database session.
        user (User): The authenticated user.

    Returns:
        ContactResponse: The ContactResponse object representing the removed contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact
