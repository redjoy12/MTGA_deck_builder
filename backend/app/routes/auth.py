"""Authentication routes for user registration and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.auth import create_access_token, get_password_hash, verify_password
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.auth_schemas import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user (UserCreate): User registration data including username, email, and password.
        db (Session): Database session dependency.

    Returns:
        UserResponse: The created user details (without password).

    Raises:
        HTTPException: If username or email already exists.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create new user with hashed password
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        ) from e


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token.

    This endpoint accepts form data with username and password.
    Compatible with OAuth2 password flow.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data with username and password.
        db (Session): Database session dependency.

    Returns:
        Token: JWT access token and token type.

    Raises:
        HTTPException: If credentials are invalid.
    """
    # Authenticate user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Login with JSON payload and get access token.

    Alternative login endpoint that accepts JSON instead of form data.

    Args:
        user_login (UserLogin): User login credentials.
        db (Session): Database session dependency.

    Returns:
        Token: JWT access token and token type.

    Raises:
        HTTPException: If credentials are invalid.
    """
    # Authenticate user
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.

    Args:
        current_user (User): The current authenticated user from the token.

    Returns:
        UserResponse: Current user details.
    """
    return current_user
