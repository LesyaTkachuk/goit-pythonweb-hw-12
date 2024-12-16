from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository.

        Args:
            session: An AsyncSession object representing the database session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The User object representing the user with the given ID, or None if not found.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(
        self, username: str, refresh_token: str | None
    ) -> User | None:
        """
        Get a user by their username.

        Args:
            username (str): The username of the user to retrieve.
            refresh_token (str | None): The refresh token of the user to retrieve.

        Returns:
            User | None: The User object representing the user with the given username, or None if not found.
        """
        stmt = select(User).filter_by(username=username)

        if refresh_token:
            stmt = stmt.filter_by(refresh_token=refresh_token)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The User object representing the user with the given email, or None if not found.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user with the provided details.

        Args:
            body (UserCreate): The UserCreate object containing the user details.
            avatar (str): The avatar URL of the user.

        Returns:
            User: The created User object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            avatar=avatar,
            hashed_password=body.password
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        Args:
            email (str): The email of the user to mark as confirmed.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()
        await self.db.refresh(user)


    async def update_avatar_url(self, email: str, avatar_url: str) -> User:
        """
        Update a user's avatar URL.

        Args:
            email (str): The email of the user to update.
            avatar_url (str): The new avatar URL for the user.

        Returns:
            User: The updated User object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user
