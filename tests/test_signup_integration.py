"""
Integration tests for signup functionality.

This module tests the complete signup flow including database
interactions and email sending.

Requirements: 2.1, 2.2, 2.3, 2.4
"""

import pytest
from src.app import create_app
from src.database import init_db, db_session, engine
from src.models import Base, User
from unittest.mock import patch, MagicMock


@pytest.fixture(scope='function')
def setup_database():
    """Set up a clean database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean up - drop all tables
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def app(setup_database):
    """Create a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_signup_post_valid_data(client):
    """
    Test that signup creates a user with valid data.
    
    Requirements: 2.2
    """
    with patch('src.email_service.send_verification_email') as mock_email:
        mock_email.return_value = True
        
        response = client.post('/signup', data={
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=False)
        
        # Should redirect to signin
        assert response.status_code == 302
        assert '/signin' in response.location
        
        # Verify user was created in database
        user = db_session.query(User).filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.is_verified is False  # Should be unverified
        
        # Verify email was sent
        mock_email.assert_called_once()


def test_signup_post_duplicate_email(client):
    """
    Test that signup rejects duplicate email addresses.
    
    Requirements: 2.3
    """
    # Create a user first
    from src.auth import register_user
    register_user('existing@example.com', 'password123')
    
    with patch('src.email_service.send_verification_email'):
        response = client.post('/signup', data={
            'email': 'existing@example.com',
            'password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'already registered' in response.data or b'already exists' in response.data


def test_signup_post_invalid_email(client):
    """
    Test that signup rejects invalid email addresses.
    
    Requirements: 2.4
    """
    response = client.post('/signup', data={
        'email': 'not-an-email',
        'password': 'SecurePass123',
        'confirm_password': 'SecurePass123'
    })
    
    # Should return 400 with error
    assert response.status_code == 400
    assert b'email' in response.data.lower()


def test_signup_post_weak_password(client):
    """
    Test that signup rejects weak passwords.
    
    Requirements: 2.4
    """
    response = client.post('/signup', data={
        'email': 'test@example.com',
        'password': 'short',
        'confirm_password': 'short'
    })
    
    # Should return 400 with error
    assert response.status_code == 400
    assert b'password' in response.data.lower()


def test_signup_post_empty_fields(client):
    """
    Test that signup rejects empty fields.
    
    Requirements: 2.4
    """
    response = client.post('/signup', data={
        'email': '',
        'password': '',
        'confirm_password': ''
    })
    
    # Should return 400 with error
    assert response.status_code == 400


def test_signup_creates_unverified_user(client):
    """
    Test that signup creates users with unverified status.
    
    Requirements: 2.2
    """
    with patch('src.email_service.send_verification_email') as mock_email:
        mock_email.return_value = True
        
        client.post('/signup', data={
            'email': 'unverified@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        })
        
        # Verify user is unverified
        user = db_session.query(User).filter_by(email='unverified@example.com').first()
        assert user is not None
        assert user.is_verified is False


def test_signup_sends_verification_email(client):
    """
    Test that signup sends a verification email.
    
    Requirements: 2.2, 3.1
    """
    with patch('src.email_service.send_verification_email') as mock_email:
        mock_email.return_value = True
        
        client.post('/signup', data={
            'email': 'verify@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        })
        
        # Verify email sending was attempted
        assert mock_email.call_count == 1
        
        # Verify the user object was passed
        call_args = mock_email.call_args[0]
        assert len(call_args) == 1
        user = call_args[0]
        assert user.email == 'verify@example.com'


def test_signup_handles_email_failure_gracefully(client):
    """
    Test that signup handles email sending failures gracefully.
    
    Requirements: 2.2
    """
    with patch('src.email_service.send_verification_email') as mock_email:
        mock_email.side_effect = Exception('SMTP error')
        
        response = client.post('/signup', data={
            'email': 'emailfail@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=False)
        
        # Should still redirect (user created)
        assert response.status_code == 302
        
        # User should still be created
        user = db_session.query(User).filter_by(email='emailfail@example.com').first()
        assert user is not None


def test_signup_password_is_hashed(client):
    """
    Test that signup stores hashed passwords, not plaintext.
    
    Requirements: 2.5
    """
    with patch('src.email_service.send_verification_email') as mock_email:
        mock_email.return_value = True
        
        password = 'SecurePass123'
        client.post('/signup', data={
            'email': 'hashed@example.com',
            'password': password,
            'confirm_password': password
        })
        
        # Verify password is hashed
        user = db_session.query(User).filter_by(email='hashed@example.com').first()
        assert user is not None
        assert user.password_hash != password
        assert len(user.password_hash) > 20  # Hashed passwords are long
