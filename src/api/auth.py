from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.services.email import send_email
from src.schemas import TokenRefreshRequest, UserCreate, Token, UserBase, RequestEmail
from src.services.auth import (
    create_access_token,
    Hash,
    create_refresh_token,
    get_email_from_token,
    verify_refresh_token,
)
from src.services.users import UserService
from src.database.db import get_db
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user

    Args:
        body: UserCreate
        background_tasks: BackgroundTasks
        request: Request
        db: AsyncSession

    Returns:
        Registered User
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(body.email)
    if email_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_EMAIL_OR_NAME_ALREADY_EXISTS,
        )

    username_user = await user_service.get_user_by_username(body.username)
    if username_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_EMAIL_OR_NAME_ALREADY_EXISTS,
        )

    body.password = Hash().get_password_hash(body.password)
    new_user = await user_service.create_user(body)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


# login
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Login a user

    Args:
        form_data: OAuth2PasswordRequestForm
        db: AsyncSession

    Returns:
        AccessToken
        RefreshToken
        TokenType
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_NOT_CONFIRMED,
        )

    # generate JWT
    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    await db.commit()
    await db.refresh(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Create new access and refresh token

    Args:
        request: TokenRefreshRequest
        db: AsyncSession

    Returns:
        AccessToken
        RefreshToken
        TokenType
    """

    user = await verify_refresh_token(request.refresh_token, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_REFRESH_TOKEN,
        )

    new_access_token = await create_access_token(data={"sub": user.username})
    new_refresh_token = await create_refresh_token(data={"sub": user.username})
    user.refresh_token = new_refresh_token
    await db.commit()
    await db.refresh(user)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


# confirm email
@router.get("/confirm-email/{token}")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm email

    Args:
        token: str
        db: AsyncSession

    Returns:
        Message User is confirmed or User  was not found
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )
    if user.confirmed:
        return {"message": messages.USER_ALREADY_CONFIRMED}
    await user_service.confirmed_email(email)
    return {"message": messages.USER_CONFIRMED}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Send confirmation email

    Args:
        body: RequestEmail
        background_tasks: BackgroundTasks
        request: Request
        db: AsyncSession

    Returns:
        Message User is already confirmed or Email with confirmation sent
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )

    if user.confirmed:
        return {"message": messages.USER_ALREADY_CONFIRMED}

    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": messages.EMAIL_SENT}
