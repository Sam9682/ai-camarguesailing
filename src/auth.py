"""
Authentication module for Camargue Sailing website.

This module provides user registration, authentication, and email verification
functionality for the application.

Requirements: 2.1, 2.2, 2.3, 2.4, 3.2, 3.5, 4.2, 4.3, 4.4, 5.1, 5.2
"""

import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from functools import wraps
from flask import session, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from src.database import db_session
from src.models import User, VerificationToken


class RegistrationError(Exception):
    """Exception raised for registration validation errors."""
    pass


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Requirements: 2.4
    """
    if not email:
        return False, "Email is required"
    
    if not isinstance(email, str):
        return False, "Email must be a string"
    
    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long (maximum 255 characters)"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password requirements.
    
    Password must:
    - Be at least 8 characters long
    - Not be empty
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Requirements: 2.4
    """
    if not password:
        return False, "Password is required"
    
    if not isinstance(password, str):
        return False, "Password must be a string"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    return True, None


def register_user(email: str, password: str) -> User:
    """
    Register a new user with unverified status.
    
    This function validates the email and password, checks for email uniqueness,
    creates a new user account with is_verified=False, and stores the hashed password.
    
    Args:
        email: User's email address
        password: User's plaintext password
    
    Returns:
        The newly created User object
    
    Raises:
        RegistrationError: If validation fails or email already exists
    
    Requirements: 2.1, 2.2, 2.3, 2.4
    """
    # Validate email format
    email_valid, email_error = validate_email(email)
    if not email_valid:
        raise RegistrationError(email_error)
    
    # Validate password requirements
    password_valid, password_error = validate_password(password)
    if not password_valid:
        raise RegistrationError(password_error)
    
    # Normalize email to lowercase for consistency
    email = email.lower().strip()
    
    # Check if email already exists
    existing_user = db_session.query(User).filter_by(email=email).first()
    if existing_user:
        raise RegistrationError("Email address is already registered")
    
    # Create new user with unverified status
    user = User(
        email=email,
        is_verified=False
    )
    user.set_password(password)
    
    try:
        db_session.add(user)
        db_session.commit()
        return user
    except IntegrityError as e:
        db_session.rollback()
        # This handles race conditions where two registrations happen simultaneously
        # Log the specific integrity error for debugging
        import logging
        logging.error(f"IntegrityError during user registration: {str(e)}")
        raise RegistrationError("Email address is already registered")
    except Exception as e:
        db_session.rollback()
        # Log unexpected database errors
        import logging
        logging.error(f"Database error during user registration: {str(e)}")
        raise RegistrationError(f"Failed to create user account: {str(e)}")


def generate_verification_token(user_id: int, expiration_hours: int = 24) -> str:
    """
    Generate a secure verification token for email verification.
    
    This function creates a cryptographically secure random token and stores it
    in the database with an expiration time. The token is URL-safe and unique.
    
    Args:
        user_id: The ID of the user for whom to generate the token
        expiration_hours: Number of hours until the token expires (default: 24)
    
    Returns:
        The generated verification token string
    
    Raises:
        ValueError: If the user_id is invalid or user doesn't exist
    
    Requirements: 3.2
    """
    # Verify user exists
    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist")
    
    # Generate a secure random token (32 bytes = 256 bits)
    # Using secrets module for cryptographically strong random numbers
    token = secrets.token_urlsafe(32)
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
    
    # Create verification token record
    verification_token = VerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    try:
        db_session.add(verification_token)
        db_session.commit()
        return token
    except IntegrityError as e:
        db_session.rollback()
        # In the extremely unlikely case of a token collision, try again
        import logging
        logging.warning(f"Token collision during verification token generation: {str(e)}")
        return generate_verification_token(user_id, expiration_hours)
    except Exception as e:
        db_session.rollback()
        # Log unexpected database errors
        import logging
        logging.error(f"Database error during verification token generation: {str(e)}")
        raise ValueError(f"Failed to generate verification token: {str(e)}")


def verify_token(token: str) -> Optional[int]:
    """
    Verify an email verification token and mark the user as verified.
    
    This function checks if the token exists, is not expired, and marks the
    associated user as verified. The token is deleted after successful verification.
    
    Args:
        token: The verification token string to verify
    
    Returns:
        The user_id if verification is successful, None if token is invalid or expired
    
    Requirements: 3.2, 3.3, 3.4
    """
    if not token:
        return None
    
    # Find the verification token
    verification_token = db_session.query(VerificationToken).filter_by(token=token).first()
    
    if not verification_token:
        return None
    
    # Check if token has expired
    if verification_token.is_expired():
        # Clean up expired token
        try:
            db_session.delete(verification_token)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            # Log but don't fail - expired token cleanup is not critical
            import logging
            logging.warning(f"Failed to delete expired verification token: {str(e)}")
        return None
    
    # Get the user and mark as verified
    user = verification_token.user
    if not user:
        return None
    
    try:
        user.is_verified = True
        # Delete the token after successful verification
        db_session.delete(verification_token)
        db_session.commit()
        return user.id
    except Exception as e:
        db_session.rollback()
        # Log the database error
        import logging
        logging.error(f"Database error during user verification: {str(e)}")
        raise ValueError(f"Failed to verify user: {str(e)}")


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass


def authenticate_user(email: str, password: str) -> User:
    """
    Authenticate a user with email and password.
    
    This function verifies the user's credentials and checks that the user's
    email has been verified. If authentication is successful, it returns the
    User object which can be used to create a session.
    
    Args:
        email: User's email address
        password: User's plaintext password
    
    Returns:
        The authenticated User object
    
    Raises:
        AuthenticationError: If credentials are incorrect or user is not verified
    
    Requirements: 4.2, 4.3, 4.4
    """
    if not email or not password:
        raise AuthenticationError("Email and password are required")
    
    # Normalize email to lowercase for consistency
    email = email.lower().strip()
    
    # Find user by email
    user = db_session.query(User).filter_by(email=email).first()
    
    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        # Use generic error message to avoid revealing whether email exists
        raise AuthenticationError("Incorrect email or password")
    
    # Check if user's email is verified
    if not user.is_verified:
        raise AuthenticationError("Email verification is required. Please check your email for the verification link.")
    
    # Authentication successful
    return user


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.
    
    This function is used for session management to load a user from their
    stored user_id in the session.
    
    Args:
        user_id: The user's ID
    
    Returns:
        The User object if found, None otherwise
    
    Requirements: 5.3
    """
    if not user_id:
        return None
    
    try:
        return db_session.query(User).filter_by(id=user_id).first()
    except Exception as e:
        # Log database errors during user lookup
        import logging
        logging.error(f"Database error during user lookup (user_id={user_id}): {str(e)}")
        return None


def login_required(f):
    """
    Decorator to require user authentication for a route.
    
    This decorator checks if a user is logged in (has a valid session with user_id).
    If not authenticated, redirects to the sign-in page. If authenticated, allows
    access to the protected route.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_page():
            return "This page requires login"
    
    Requirements: 5.1, 5.2
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id exists in session
        user_id = session.get('user_id')
        
        if not user_id:
            # User is not logged in, redirect to sign-in page
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('signin'))
        
        # User is logged in, allow access
        return f(*args, **kwargs)
    
    return decorated_function


def verified_required(f):
    """
    Decorator to require verified user authentication for a route.
    
    This decorator checks if a user is logged in AND has verified their email.
    If not authenticated, redirects to sign-in page. If authenticated but not
    verified, redirects to a verification required page or shows an error.
    
    This decorator should be used in combination with @login_required or can
    be used standalone (it includes login checking).
    
    Usage:
        @app.route('/protected')
        @verified_required
        def protected_page():
            return "This page requires verified account"
    
    Requirements: 3.5, 5.1, 5.2
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id exists in session
        user_id = session.get('user_id')
        
        if not user_id:
            # User is not logged in, redirect to sign-in page
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('signin'))
        
        # Get user from database to check verification status
        user = get_user_by_id(user_id)
        
        if not user:
            # User not found in database, clear session and redirect
            session.clear()
            flash('Session expired. Please sign in again.', 'warning')
            return redirect(url_for('signin'))
        
        if not user.is_verified:
            # User is not verified, deny access
            flash('Email verification is required to access this page. Please check your email for the verification link.', 'error')
            return redirect(url_for('home'))
        
        # User is logged in and verified, allow access
        return f(*args, **kwargs)
    
    return decorated_function
