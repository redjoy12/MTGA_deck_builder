"""Dependencies for authentication and authorization."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth import decode_access_token
from app.core.database import get_db
from app.models.user import User
from app.models.auth_schemas import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from a JWT token.

    Args:
        token (str): The JWT token from the Authorization header.
        db (Session): Database session dependency.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract username from token
    username: Optional[str] = payload.get("sub")
    user_id: Optional[int] = payload.get("user_id")

    if username is None:
        raise credentials_exception

    token_data = TokenData(username=username, user_id=user_id)

    # Get user from database
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        User: The current active user.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to verify the current user is a superuser.

    Args:
        current_user (User): The current active user.

    Returns:
        User: The current superuser.

    Raises:
        HTTPException: If the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
