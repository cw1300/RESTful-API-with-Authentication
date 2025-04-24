"""
User routes for the Task Management API.
Handles user profile operations and admin functions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr

from app.models.user import User
from app.middleware.auth_middleware import get_current_active_user, get_current_admin_user
from config.config import get_db

router = APIRouter()

# Pydantic models for request/response
class UserUpdate(BaseModel):
    """Schema for user update request."""
    full_name: str = None
    email: EmailStr = None

class UserResponse(BaseModel):
    """Schema for user response data."""
    id: int
    username: str
    email: str
    full_name: str = None
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current user's profile.

    Args:
        current_user: The authenticated user

    Returns:
        UserResponse: The user's profile data
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile.

    Args:
        user_data: Profile update data
        current_user: The authenticated user
        db: Database session

    Returns:
        UserResponse: The updated user profile
    """
    # Update email if provided and check if it's already taken
    if user_data.email and user_data.email != current_user.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_data.email

    # Update full name if provided
    if user_data.full_name:
        current_user.full_name = user_data.full_name

    db.commit()
    db.refresh(current_user)

    return current_user

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only).

    Args:
        current_user: The authenticated admin user
        db: Database session

    Returns:
        List[UserResponse]: List of all users
    """
    users = db.query(User).all()
    return users

@router.put("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (admin only).

    Args:
        user_id: The ID of the user to deactivate
        current_user: The authenticated admin user
        db: Database session

    Returns:
        UserResponse: The deactivated user

    Raises:
        HTTPException: If user not found or trying to deactivate self
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()
    db.refresh(user)

    return user

@router.put("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate a user (admin only).

    Args:
        user_id: The ID of the user to activate
        current_user: The authenticated admin user
        db: Database session

    Returns:
        UserResponse: The activated user

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)

    return user