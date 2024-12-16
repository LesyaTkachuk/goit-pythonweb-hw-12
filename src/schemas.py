from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from src.database.models import UserRole


class UserBase(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    role: UserRole | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=50)
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=8, max_length=12)
    role: UserRole | None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RequestEmail(BaseModel):
    email: EmailStr


class GroupModel(BaseModel):
    name: str = Field(max_length=50)


class GroupResponse(GroupModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    surname: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=150)
    phone_number: str = Field(min_length=3, max_length=20)
    birthday: date = Field(default=None)


class ContactModel(ContactBase):
    groups: List[int]


class ContactUpdate(ContactModel):
    is_active: bool


class ContactIsActiveUpdate(BaseModel):
    is_active: bool


class ContactResponse(ContactModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] | None
    is_active: bool
    address_id: Optional[int]
    groups: List[GroupResponse] | None

    model_config = ConfigDict(from_attributes=True)
