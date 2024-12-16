from datetime import datetime, date
from typing import Optional
from enum import Enum
from sqlalchemy import (
    Column,
    Enum as SQLAlchemyEnum,
    Integer,
    String,
    Boolean,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime, Date


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    avatar: Mapped[str] = mapped_column(String(200), nullable=True)
    confirmed: Mapped[bool] = mapped_column(
        "confirmed", Boolean, default=False, nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole, name="user_roles_enum"),
        default=UserRole.USER,
        nullable=False,
    )
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="user")
    groups: Mapped[list["Group"]] = relationship("Group", back_populates="user")


contact_m2m_group = Table(
    "contact_m2m_group",
    Base.metadata,
    Column(
        "contact_id",
        Integer,
        ForeignKey("contact.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
    Column(
        "group_id",
        Integer,
        ForeignKey("group.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
    PrimaryKeyConstraint("contact_id", "group_id"),
)


class Contact(Base):
    __tablename__ = "contact"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    surname: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), default=None, nullable=True
    )
    user: Mapped["User"] = relationship("User", back_populates="contacts")
    address_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("address.id"), nullable=True, default=None
    )
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    groups: Mapped[list["Group"]] = relationship(
        "Group", secondary=contact_m2m_group, back_populates="contacts"
    )


class Group(Base):
    __tablename__ = "group"
    __table_args__ = (UniqueConstraint("name", "user_id", name="unique_group_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(50), nullable=False)
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", secondary=contact_m2m_group, back_populates="groups"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), default=None, nullable=True
    )
    user: Mapped["User"] = relationship("User", back_populates="groups")


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    street: Mapped[str] = mapped_column(String(50), nullable=False)
    house: Mapped[str] = mapped_column(String(4), nullable=False)
    apartment: Mapped[str] = mapped_column(String(4))
