import redis
import json
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.schemas import UserBase
from src.database.models import Contact, Group, UserRole, User
from src.database.db import get_db
from src.conf.config import config
from src.conf import messages
from src.services.users import UserService


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# define a function to generate a new access token
async def create_token(
    data: dict, token_type: Literal["access", "refresh"], expires_delta: timedelta
):
    """
    Create a new access or refresh token.

    Args:
        data (dict): The data to be included in the token.
        token_type (str): The type of token to be created.
        expires_delta (timedelta): The expiration time for the token.

    Returns:
        str: The generated token.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=expires_delta)

    to_encode.update({"exp": expire, "iat": now, "token_type": token_type})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


# define a function to create a new access token
async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a new access token.

    Args:
        data (dict): The data to be included in the token.
        expires_delta (timedelta): The expiration time for the token.

    Returns:
        str: The generated access token.
    """
    if expires_delta:
        access_token = await create_token(data, "access", expires_delta)
    else:
        access_token = await create_token(data, "access", config.JWT_EXPIRATION_SECONDS)
    return access_token


# define a function to create a new refresh token
async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a new refresh token.

    Args:
        data (dict): The data to be included in the token.
        expires_delta (timedelta): The expiration time for the token.

    Returns:
        str: The generated refresh token.
    """
    if expires_delta:
        refresh_token = await create_token(data, "refresh", expires_delta)
    else:
        refresh_token = await create_token(
            data, "refresh", config.JWT_REFRESH_EXPIRATION_SECONDS
        )
    return refresh_token


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Get the current user based on the provided token.

    Args:
        token (str): The token to be used to get the current user.
        db (Session): The database session to be used to get the current user.

    Returns:
        User: The current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=messages.UNVERIFIED_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # decode JWT
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        token_type = payload.get("token_type")
        if username is None or token_type != "access":
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    # Connecting to Redis
    redis_connector = redis.Redis(
        host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB
    )
    retrieved_user_json = redis_connector.get(str(username))
    if retrieved_user_json:
        user = json.loads(retrieved_user_json)
        contacts = await db.execute(select(Contact).filter_by(user_id=user["id"]))
        groups = await db.execute(select(Group).filter_by(user_id=user["id"]))
        user = User(
            **user, contacts=contacts.scalars().all(), groups=groups.scalars().all()
        )

    else:
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username=username)
        if user is None:
            raise credentials_exception

        user_json = UserBase.model_validate(user).model_dump_json(
            exclude=["contacts", "groups"]
        )
        redis_connector.set(str(username), user_json)
        redis_connector.expire(str(username), config.REDIS_EXPIRATION_TIME)

    return user


async def verify_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Verify the refresh token.

    Args:
        refresh_token (str): The refresh token to be verified.
        db (Session): The database session to be used to verify the refresh token.

    Returns:
        User: The user associated with the refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=messages.UNVERIFIED_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            refresh_token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        token_type = payload.get("token_type")
        if username is None or token_type != "refresh":
            raise credentials_exception
        user = await UserService(db).get_user_by_username(username, refresh_token)
        return user
    except JWTError as e:
        raise credentials_exception


def create_email_token(data: dict):
    """
    Create a new email token.

    Args:
        data (dict): The data to be included in the token.

    Returns:
        str: The generated email token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    token = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Get the email from the token.

    Args:
        token (str): The token to be used to get the email.

    Returns:
        str: The email associated with the token.
    """
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.UNEXISTING_TOKEN,
        )


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.INSUFFICIENT_PERMISSIONS,
        )
    return current_user
