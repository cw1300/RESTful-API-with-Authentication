"""
Validation utilities for the Task Management API.
Provides functions for input validation and data sanitization.
"""

import re
from typing import Optional
from fastapi import HTTPException, status

def validate_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def validate_password(password: str) -> bool:
    """
    Validate password strength.
    Password must be at least 8 characters and contain:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        bool: True if password meets requirements, False otherwise
    """
    if len(password) < 8:
        return False

    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return has_upper and has_lower and has_digit and has_special

def validate_username(username: str) -> bool:
    """
    Validate username format.
    Username must be 3-50 characters and contain only letters, numbers, and underscores.

    Args:
        username: Username to validate

    Returns:
        bool: True if username is valid, False otherwise
    """
    if not (3 <= len(username) <= 50):
        return False

    username_regex = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(username_regex, username))

def sanitize_string(input_string: Optional[str]) -> Optional[str]:
    """
    Sanitize string input by removing potentially harmful characters.

    Args:
        input_string: String to sanitize

    Returns:
        str: Sanitized string or None if input is None
    """
    if input_string is None:
        return None

    # Remove HTML tags
    sanitized = re.sub(r'<[^>]*>', '', input_string)
    # Remove multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Trim whitespace
    sanitized = sanitized.strip()

    return sanitized

def validate_registration_data(username: str, email: str, password: str) -> None:
    """
    Validate user registration data and raise exceptions if invalid.

    Args:
        username: Username to validate
        email: Email to validate
        password: Password to validate

    Raises:
        HTTPException: If any validation fails
    """
    if not validate_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be 3-50 characters and contain only letters, numbers, and underscores"
        )

    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address"
        )

    if not validate_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and contain uppercase, lowercase, number, and special character"
        )