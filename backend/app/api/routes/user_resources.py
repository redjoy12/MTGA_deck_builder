"""API routes for user resources (wildcards and currency)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.database import get_db
from app.models.user_resources import UserResources
from app.models.schemas import (
    UserResourcesCreate,
    UserResourcesUpdate,
    UserResourcesResponse,
    WildcardUpdate,
    CurrencyUpdate
)

router = APIRouter(
    prefix="/api/users",
    tags=["User Resources"]
)


@router.post(
    "/{user_id}/resources",
    response_model=UserResourcesResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user_resources(
    user_id: str,
    resources: UserResourcesCreate,
    db: Session = Depends(get_db)
):
    """
    Create initial resources for a user.

    Args:
        user_id (str): The user identifier
        resources (UserResourcesCreate): Initial resource values
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The created user resources

    Raises:
        HTTPException: If resources already exist or database error occurs
    """
    try:
        # Check if resources already exist
        existing = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resources already exist for user {user_id}"
            )

        db_resources = UserResources(user_id=user_id, **resources.dict(exclude={'user_id'}))
        db.add(db_resources)
        db.commit()
        db.refresh(db_resources)
        return db_resources
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User resources already exist: {str(e)}"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@router.get(
    "/{user_id}/resources",
    response_model=UserResourcesResponse
)
def get_user_resources(user_id: str, db: Session = Depends(get_db)):
    """
    Get user's current resources.

    Args:
        user_id (str): The user identifier
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The user's current resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            # Auto-create default resources for new users
            resources = UserResources(user_id=user_id)
            db.add(resources)
            db.commit()
            db.refresh(resources)
        return resources
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@router.put(
    "/{user_id}/resources",
    response_model=UserResourcesResponse
)
def update_user_resources(
    user_id: str,
    updates: UserResourcesUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user's resources.

    Args:
        user_id (str): The user identifier
        updates (UserResourcesUpdate): Resource updates
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The updated resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resources not found for user {user_id}"
            )

        # Update fields
        for key, value in updates.dict(exclude_unset=True).items():
            if value is not None:
                setattr(resources, key, value)

        db.commit()
        db.refresh(resources)
        return resources
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@router.patch(
    "/{user_id}/resources/wildcards",
    response_model=UserResourcesResponse
)
def update_wildcards(
    user_id: str,
    wildcard: WildcardUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific wildcard amount.

    Args:
        user_id (str): The user identifier
        wildcard (WildcardUpdate): Wildcard rarity and new amount
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The updated resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resources not found for user {user_id}"
            )

        resources.update_wildcards(wildcard.rarity.value, wildcard.amount)
        db.commit()
        db.refresh(resources)
        return resources
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@router.patch(
    "/{user_id}/resources/currency",
    response_model=UserResourcesResponse
)
def update_currency(
    user_id: str,
    currency: CurrencyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user's currency (gold and/or gems).

    Args:
        user_id (str): The user identifier
        currency (CurrencyUpdate): Currency updates
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The updated resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resources not found for user {user_id}"
            )

        resources.update_currency(gold=currency.gold, gems=currency.gems)
        db.commit()
        db.refresh(resources)
        return resources
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e
