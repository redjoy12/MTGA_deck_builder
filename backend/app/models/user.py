"""SQLAlchemy model for User authentication."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func

from app.core.database import Base


class User(Base):
    """
    SQLAlchemy model representing a user with authentication capabilities.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The unique username for the user.
        email (str): The unique email address for the user.
        hashed_password (str): The hashed password for authentication.
        is_active (bool): Whether the user account is active.
        is_superuser (bool): Whether the user has superuser privileges.
        created_at (datetime): The date and time the user was created.
        updated_at (datetime): The date and time the user was last updated.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
