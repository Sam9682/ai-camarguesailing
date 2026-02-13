"""
Unit tests for database models.

This module tests the User model including password hashing functionality.

Requirements: 2.2, 2.5
"""

import pytest
from src.models import User
from src.database import Base, engine, db_session


@pytest.fixture(scope='function')
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


def test_user_creation(setup_database):
    """Test that a User can be created with required fields."""
    user = User(email='test@example.com')
    user.set_password('securepassword123')
    
    db_session.add(user)
    db_session.commit()
    
    # Verify user was created
    assert user.id is not None
    assert user.email == 'test@example.com'
    assert user.password_hash is not None
    assert user.password_hash != 'securepassword123'  # Password should be hashed
    assert user.is_verified is False  # Default value
    assert user.created_at is not None
    assert user.updated_at is not None


def test_password_hashing(setup_database):
    """Test that passwords are hashed and not stored in plaintext."""
    user = User(email='test@example.com')
    plaintext_password = 'mySecretPassword123'
    user.set_password(plaintext_password)
    
    # Password hash should not equal plaintext
    assert user.password_hash != plaintext_password
    # Password hash should be a non-empty string
    assert len(user.password_hash) > 0


def test_password_verification_success(setup_database):
    """Test that correct password verification succeeds."""
    user = User(email='test@example.com')
    password = 'correctPassword123'
    user.set_password(password)
    
    # Correct password should verify
    assert user.check_password(password) is True


def test_password_verification_failure(setup_database):
    """Test that incorrect password verification fails."""
    user = User(email='test@example.com')
    user.set_password('correctPassword123')
    
    # Incorrect password should not verify
    assert user.check_password('wrongPassword') is False


def test_unique_email_constraint(setup_database):
    """Test that duplicate emails are rejected by the database."""
    user1 = User(email='duplicate@example.com')
    user1.set_password('password1')
    db_session.add(user1)
    db_session.commit()
    
    # Try to create another user with the same email
    user2 = User(email='duplicate@example.com')
    user2.set_password('password2')
    db_session.add(user2)
    
    # Should raise an integrity error
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_user_repr(setup_database):
    """Test the string representation of a User."""
    user = User(email='test@example.com')
    assert repr(user) == '<User test@example.com>'
