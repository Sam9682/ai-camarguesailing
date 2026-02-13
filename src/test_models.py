"""
Unit tests for database models.

This module tests the User model including password hashing functionality.

Requirements: 2.2, 2.5
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.models import User
from src.database import Base


@pytest.fixture(scope='function')
def test_db():
    """Create an in-memory SQLite database for testing."""
    # Create in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    
    yield session
    
    # Cleanup
    session.remove()
    Base.metadata.drop_all(bind=engine)


def test_user_creation(test_db):
    """Test that a User can be created with required fields."""
    user = User(email='test@example.com')
    user.set_password('securepassword123')
    
    test_db.add(user)
    test_db.commit()
    
    # Verify user was created
    assert user.id is not None
    assert user.email == 'test@example.com'
    assert user.password_hash is not None
    assert user.password_hash != 'securepassword123'  # Password should be hashed
    assert user.is_verified is False  # Default value
    assert user.created_at is not None
    assert user.updated_at is not None


def test_password_hashing(test_db):
    """Test that passwords are hashed and not stored in plaintext."""
    user = User(email='test@example.com')
    plaintext_password = 'mySecretPassword123'
    user.set_password(plaintext_password)
    
    # Password hash should not equal plaintext
    assert user.password_hash != plaintext_password
    # Password hash should be a non-empty string
    assert len(user.password_hash) > 0


def test_password_verification_success(test_db):
    """Test that correct password verification succeeds."""
    user = User(email='test@example.com')
    password = 'correctPassword123'
    user.set_password(password)
    
    # Correct password should verify
    assert user.check_password(password) is True


def test_password_verification_failure(test_db):
    """Test that incorrect password verification fails."""
    user = User(email='test@example.com')
    user.set_password('correctPassword123')
    
    # Incorrect password should not verify
    assert user.check_password('wrongPassword') is False


def test_unique_email_constraint(test_db):
    """Test that duplicate emails are rejected by the database."""
    user1 = User(email='duplicate@example.com')
    user1.set_password('password1')
    test_db.add(user1)
    test_db.commit()
    
    # Try to create another user with the same email
    user2 = User(email='duplicate@example.com')
    user2.set_password('password2')
    test_db.add(user2)
    
    # Should raise an integrity error
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        test_db.commit()


def test_user_repr(test_db):
    """Test the string representation of a User."""
    user = User(email='test@example.com')
    assert repr(user) == '<User test@example.com>'
