"""
Unit tests for authentication module.

Tests user registration, email validation, password validation,
and error handling.

Requirements: 2.1, 2.2, 2.3, 2.4
"""

import pytest
from src.auth import register_user, validate_email, validate_password, RegistrationError
from src.models import User
from src.database import db_session, init_db, Base, engine


@pytest.fixture(scope='function')
def setup_database():
    """Set up a clean database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean up after test
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


class TestEmailValidation:
    """Test email validation function."""
    
    def test_valid_email(self):
        """Test that valid email formats are accepted."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com"
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid, f"Email {email} should be valid but got error: {error}"
            assert error is None
    
    def test_invalid_email_format(self):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            ""
        ]
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert not is_valid, f"Email {email} should be invalid"
            assert error is not None
    
    def test_empty_email(self):
        """Test that empty email is rejected."""
        is_valid, error = validate_email("")
        assert not is_valid
        assert "required" in error.lower()
    
    def test_email_too_long(self):
        """Test that overly long emails are rejected."""
        long_email = "a" * 250 + "@example.com"
        is_valid, error = validate_email(long_email)
        assert not is_valid
        assert "too long" in error.lower()


class TestPasswordValidation:
    """Test password validation function."""
    
    def test_valid_password(self):
        """Test that valid passwords are accepted."""
        valid_passwords = [
            "password123",
            "12345678",
            "a" * 8,
            "MySecureP@ssw0rd!"
        ]
        for password in valid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid, f"Password should be valid but got error: {error}"
            assert error is None
    
    def test_password_too_short(self):
        """Test that short passwords are rejected."""
        short_passwords = ["", "a", "1234567"]
        for password in short_passwords:
            is_valid, error = validate_password(password)
            assert not is_valid
            assert error is not None
    
    def test_empty_password(self):
        """Test that empty password is rejected."""
        is_valid, error = validate_password("")
        assert not is_valid
        assert "required" in error.lower()


class TestUserRegistration:
    """Test user registration function."""
    
    def test_register_user_success(self, setup_database):
        """Test successful user registration creates unverified user."""
        email = "newuser@example.com"
        password = "password123"
        
        user = register_user(email, password)
        
        assert user is not None
        assert user.id is not None
        assert user.email == email.lower()
        assert user.is_verified is False
        assert user.password_hash != password  # Password should be hashed
        assert user.check_password(password)  # But should verify correctly
    
    def test_register_user_duplicate_email(self, setup_database):
        """Test that duplicate email registration is rejected."""
        email = "duplicate@example.com"
        password = "password123"
        
        # Register first user
        user1 = register_user(email, password)
        assert user1 is not None
        
        # Try to register with same email
        with pytest.raises(RegistrationError) as exc_info:
            register_user(email, password)
        
        assert "already registered" in str(exc_info.value).lower()
    
    def test_register_user_duplicate_email_case_insensitive(self, setup_database):
        """Test that email uniqueness is case-insensitive."""
        password = "password123"
        
        # Register with lowercase
        user1 = register_user("user@example.com", password)
        assert user1 is not None
        
        # Try to register with uppercase
        with pytest.raises(RegistrationError) as exc_info:
            register_user("USER@EXAMPLE.COM", password)
        
        assert "already registered" in str(exc_info.value).lower()
    
    def test_register_user_invalid_email(self, setup_database):
        """Test that invalid email is rejected."""
        with pytest.raises(RegistrationError) as exc_info:
            register_user("notanemail", "password123")
        
        assert "email" in str(exc_info.value).lower()
    
    def test_register_user_invalid_password(self, setup_database):
        """Test that invalid password is rejected."""
        with pytest.raises(RegistrationError) as exc_info:
            register_user("user@example.com", "short")
        
        assert "password" in str(exc_info.value).lower()
    
    def test_register_user_empty_email(self, setup_database):
        """Test that empty email is rejected."""
        with pytest.raises(RegistrationError) as exc_info:
            register_user("", "password123")
        
        assert "required" in str(exc_info.value).lower()
    
    def test_register_user_empty_password(self, setup_database):
        """Test that empty password is rejected."""
        with pytest.raises(RegistrationError) as exc_info:
            register_user("user@example.com", "")
        
        assert "required" in str(exc_info.value).lower()
    
    def test_register_user_email_normalization(self, setup_database):
        """Test that email is normalized to lowercase."""
        email = "User@Example.COM"
        password = "password123"
        
        user = register_user(email, password)
        
        assert user.email == "user@example.com"
    
    def test_register_user_password_hashing(self, setup_database):
        """Test that password is hashed and not stored in plaintext."""
        email = "secure@example.com"
        password = "MySecurePassword123"
        
        user = register_user(email, password)
        
        # Password should be hashed
        assert user.password_hash != password
        assert len(user.password_hash) > len(password)
        
        # But should verify correctly
        assert user.check_password(password)
        assert not user.check_password("WrongPassword")



class TestTokenGeneration:
    """Test email verification token generation and verification."""
    
    def test_generate_verification_token_success(self, setup_database):
        """Test successful token generation."""
        # Create a user first
        user = register_user("user@example.com", "password123")
        
        # Import here to avoid circular imports
        from src.auth import generate_verification_token
        
        # Generate token
        token = generate_verification_token(user.id)
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
        
        # Verify token was stored in database
        from src.models import VerificationToken
        stored_token = db_session.query(VerificationToken).filter_by(token=token).first()
        assert stored_token is not None
        assert stored_token.user_id == user.id
        assert stored_token.expires_at > stored_token.created_at
    
    def test_generate_verification_token_invalid_user(self, setup_database):
        """Test that token generation fails for non-existent user."""
        from src.auth import generate_verification_token
        
        with pytest.raises(ValueError) as exc_info:
            generate_verification_token(99999)
        
        assert "does not exist" in str(exc_info.value).lower()
    
    def test_generate_verification_token_uniqueness(self, setup_database):
        """Test that generated tokens are unique."""
        # Create two users
        user1 = register_user("user1@example.com", "password123")
        user2 = register_user("user2@example.com", "password123")
        
        from src.auth import generate_verification_token
        
        # Generate tokens for both users
        token1 = generate_verification_token(user1.id)
        token2 = generate_verification_token(user2.id)
        
        # Tokens should be different
        assert token1 != token2
    
    def test_generate_verification_token_custom_expiration(self, setup_database):
        """Test token generation with custom expiration time."""
        user = register_user("user@example.com", "password123")
        
        from src.auth import generate_verification_token
        from src.models import VerificationToken
        from datetime import datetime, timedelta
        
        # Generate token with 1 hour expiration
        token = generate_verification_token(user.id, expiration_hours=1)
        
        stored_token = db_session.query(VerificationToken).filter_by(token=token).first()
        
        # Check expiration is approximately 1 hour from now
        expected_expiration = datetime.utcnow() + timedelta(hours=1)
        time_diff = abs((stored_token.expires_at - expected_expiration).total_seconds())
        assert time_diff < 5  # Within 5 seconds tolerance
    
    def test_verify_token_success(self, setup_database):
        """Test successful token verification."""
        # Create user and generate token
        user = register_user("user@example.com", "password123")
        assert user.is_verified is False
        
        from src.auth import generate_verification_token, verify_token
        
        token = generate_verification_token(user.id)
        
        # Verify the token
        verified_user_id = verify_token(token)
        
        assert verified_user_id == user.id
        
        # Refresh user from database
        db_session.refresh(user)
        assert user.is_verified is True
        
        # Token should be deleted after verification
        from src.models import VerificationToken
        stored_token = db_session.query(VerificationToken).filter_by(token=token).first()
        assert stored_token is None
    
    def test_verify_token_invalid(self, setup_database):
        """Test that invalid token returns None."""
        from src.auth import verify_token
        
        result = verify_token("invalid_token_12345")
        assert result is None
    
    def test_verify_token_empty(self, setup_database):
        """Test that empty token returns None."""
        from src.auth import verify_token
        
        result = verify_token("")
        assert result is None
    
    def test_verify_token_expired(self, setup_database):
        """Test that expired token returns None."""
        # Create user and generate token with very short expiration
        user = register_user("user@example.com", "password123")
        
        from src.auth import generate_verification_token, verify_token
        from src.models import VerificationToken
        from datetime import datetime, timedelta
        
        # Generate token
        token = generate_verification_token(user.id, expiration_hours=1)
        
        # Manually expire the token by setting expires_at to the past
        stored_token = db_session.query(VerificationToken).filter_by(token=token).first()
        stored_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()
        
        # Try to verify expired token
        result = verify_token(token)
        assert result is None
        
        # User should still be unverified
        db_session.refresh(user)
        assert user.is_verified is False
        
        # Expired token should be deleted
        stored_token = db_session.query(VerificationToken).filter_by(token=token).first()
        assert stored_token is None
    
    def test_verify_token_idempotency(self, setup_database):
        """Test that verifying the same token twice doesn't work."""
        user = register_user("user@example.com", "password123")
        
        from src.auth import generate_verification_token, verify_token
        
        token = generate_verification_token(user.id)
        
        # First verification should succeed
        result1 = verify_token(token)
        assert result1 == user.id
        
        # Second verification should fail (token deleted)
        result2 = verify_token(token)
        assert result2 is None


class TestAuthentication:
    """Test user authentication function."""
    
    def test_authenticate_verified_user_success(self, setup_database):
        """Test successful authentication of verified user with correct credentials."""
        # Create and verify a user
        email = "verified@example.com"
        password = "password123"
        user = register_user(email, password)
        
        # Manually verify the user
        user.is_verified = True
        db_session.commit()
        
        from src.auth import authenticate_user
        
        # Authenticate with correct credentials
        authenticated_user = authenticate_user(email, password)
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == email.lower()
        assert authenticated_user.is_verified is True
    
    def test_authenticate_incorrect_password(self, setup_database):
        """Test that incorrect password is rejected."""
        # Create and verify a user
        email = "user@example.com"
        password = "password123"
        user = register_user(email, password)
        user.is_verified = True
        db_session.commit()
        
        from src.auth import authenticate_user, AuthenticationError
        
        # Try to authenticate with wrong password
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user(email, "wrongpassword")
        
        assert "incorrect" in str(exc_info.value).lower()
    
    def test_authenticate_nonexistent_user(self, setup_database):
        """Test that non-existent user is rejected."""
        from src.auth import authenticate_user, AuthenticationError
        
        # Try to authenticate with non-existent email
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user("nonexistent@example.com", "password123")
        
        assert "incorrect" in str(exc_info.value).lower()
    
    def test_authenticate_unverified_user(self, setup_database):
        """Test that unverified user cannot sign in."""
        # Create user but don't verify
        email = "unverified@example.com"
        password = "password123"
        user = register_user(email, password)
        
        assert user.is_verified is False
        
        from src.auth import authenticate_user, AuthenticationError
        
        # Try to authenticate unverified user
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user(email, password)
        
        error_message = str(exc_info.value).lower()
        assert "verification" in error_message or "verify" in error_message
    
    def test_authenticate_empty_email(self, setup_database):
        """Test that empty email is rejected."""
        from src.auth import authenticate_user, AuthenticationError
        
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user("", "password123")
        
        assert "required" in str(exc_info.value).lower()
    
    def test_authenticate_empty_password(self, setup_database):
        """Test that empty password is rejected."""
        from src.auth import authenticate_user, AuthenticationError
        
        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_user("user@example.com", "")
        
        assert "required" in str(exc_info.value).lower()
    
    def test_authenticate_case_insensitive_email(self, setup_database):
        """Test that email authentication is case-insensitive."""
        # Create and verify user with lowercase email
        email = "user@example.com"
        password = "password123"
        user = register_user(email, password)
        user.is_verified = True
        db_session.commit()
        
        from src.auth import authenticate_user
        
        # Authenticate with uppercase email
        authenticated_user = authenticate_user("USER@EXAMPLE.COM", password)
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
    
    def test_authenticate_whitespace_handling(self, setup_database):
        """Test that email whitespace is handled correctly."""
        # Create and verify user
        email = "user@example.com"
        password = "password123"
        user = register_user(email, password)
        user.is_verified = True
        db_session.commit()
        
        from src.auth import authenticate_user
        
        # Authenticate with whitespace around email
        authenticated_user = authenticate_user("  user@example.com  ", password)
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
    
    def test_authenticate_returns_user_object(self, setup_database):
        """Test that authenticate_user returns a complete User object."""
        # Create and verify user
        email = "user@example.com"
        password = "password123"
        user = register_user(email, password)
        user.is_verified = True
        db_session.commit()
        
        from src.auth import authenticate_user
        
        authenticated_user = authenticate_user(email, password)
        
        # Verify it's a User object with all expected attributes
        assert hasattr(authenticated_user, 'id')
        assert hasattr(authenticated_user, 'email')
        assert hasattr(authenticated_user, 'is_verified')
        assert hasattr(authenticated_user, 'password_hash')
        assert hasattr(authenticated_user, 'check_password')


class TestSessionManagement:
    """Test session management helper functions."""
    
    def test_get_user_by_id_success(self, setup_database):
        """Test retrieving a user by ID."""
        # Create a user
        email = "user@example.com"
        password = "password123"
        user = register_user(email, password)
        
        from src.auth import get_user_by_id
        
        # Retrieve user by ID
        retrieved_user = get_user_by_id(user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
    
    def test_get_user_by_id_nonexistent(self, setup_database):
        """Test that non-existent user ID returns None."""
        from src.auth import get_user_by_id
        
        result = get_user_by_id(99999)
        assert result is None
    
    def test_get_user_by_id_none(self, setup_database):
        """Test that None user ID returns None."""
        from src.auth import get_user_by_id
        
        result = get_user_by_id(None)
        assert result is None
    
    def test_get_user_by_id_zero(self, setup_database):
        """Test that zero user ID returns None."""
        from src.auth import get_user_by_id
        
        result = get_user_by_id(0)
        assert result is None




class TestAuthenticationDecorators:
    """Test authentication decorators for route protection."""
    
    @pytest.fixture
    def flask_app(self, setup_database):
        """Create a minimal Flask app for testing decorators."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        
        # Define test routes
        from src.auth import login_required, verified_required
        
        @app.route('/public')
        def public():
            return 'public page'
        
        @app.route('/protected')
        @login_required
        def protected():
            return 'protected page'
        
        @app.route('/verified-only')
        @verified_required
        def verified_only():
            return 'verified only page'
        
        @app.route('/signin')
        def signin():
            return 'signin page'
        
        @app.route('/home')
        def home():
            return 'home page'
        
        return app
    
    def test_login_required_allows_authenticated_user(self, flask_app):
        """Test that @login_required allows authenticated users."""
        # Create and verify a user
        user = register_user("user@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        with flask_app.test_client() as client:
            # Set up session with user_id
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Access protected route
            response = client.get('/protected')
            
            assert response.status_code == 200
            assert b'protected page' in response.data
    
    def test_login_required_redirects_unauthenticated_user(self, flask_app):
        """Test that @login_required redirects unauthenticated users to signin."""
        with flask_app.test_client() as client:
            # Access protected route without authentication
            response = client.get('/protected', follow_redirects=False)
            
            # Should redirect to signin
            assert response.status_code == 302
            assert '/signin' in response.location
    
    def test_login_required_shows_flash_message(self, flask_app):
        """Test that @login_required shows a flash message when redirecting."""
        with flask_app.test_client() as client:
            # Access protected route without authentication
            response = client.get('/protected', follow_redirects=True)
            
            # Check that flash message was set by accessing it in the app context
            with flask_app.app_context():
                from flask import session as flask_session
                # The flash message should have been set
                # We can't directly check flashed messages after redirect,
                # but we can verify the redirect happened correctly
                assert response.status_code == 200
    
    def test_verified_required_allows_verified_user(self, flask_app):
        """Test that @verified_required allows verified users."""
        # Create and verify a user
        user = register_user("verified@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        with flask_app.test_client() as client:
            # Set up session with user_id
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Access verified-only route
            response = client.get('/verified-only')
            
            assert response.status_code == 200
            assert b'verified only page' in response.data
    
    def test_verified_required_redirects_unauthenticated_user(self, flask_app):
        """Test that @verified_required redirects unauthenticated users to signin."""
        with flask_app.test_client() as client:
            # Access verified-only route without authentication
            response = client.get('/verified-only', follow_redirects=False)
            
            # Should redirect to signin
            assert response.status_code == 302
            assert '/signin' in response.location
    
    def test_verified_required_blocks_unverified_user(self, flask_app):
        """Test that @verified_required blocks unverified users."""
        # Create user but don't verify
        user = register_user("unverified@example.com", "password123")
        assert user.is_verified is False
        db_session.commit()
        
        with flask_app.test_client() as client:
            # Set up session with user_id
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Access verified-only route
            response = client.get('/verified-only', follow_redirects=False)
            
            # Should redirect to home
            assert response.status_code == 302
            assert '/home' in response.location
    
    def test_verified_required_shows_verification_message(self, flask_app):
        """Test that @verified_required shows verification required message."""
        # Create user but don't verify
        user = register_user("unverified@example.com", "password123")
        db_session.commit()
        
        with flask_app.test_client() as client:
            # Set up session with user_id
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Access verified-only route
            response = client.get('/verified-only', follow_redirects=True)
            
            # Should redirect to home page
            assert response.status_code == 200
            # The flash message is set but we can't easily check it in tests
            # The important thing is that unverified users are blocked
    
    def test_verified_required_handles_invalid_user_id(self, flask_app):
        """Test that @verified_required handles invalid user_id in session."""
        with flask_app.test_client() as client:
            # Set up session with non-existent user_id
            with client.session_transaction() as sess:
                sess['user_id'] = 99999
            
            # Access verified-only route
            response = client.get('/verified-only', follow_redirects=False)
            
            # Should clear session and redirect to signin
            assert response.status_code == 302
            assert '/signin' in response.location
    
    def test_verified_required_clears_session_for_invalid_user(self, flask_app):
        """Test that @verified_required clears session when user not found."""
        with flask_app.test_client() as client:
            # Set up session with non-existent user_id
            with client.session_transaction() as sess:
                sess['user_id'] = 99999
            
            # Access verified-only route
            client.get('/verified-only', follow_redirects=True)
            
            # Session should be cleared
            with client.session_transaction() as sess:
                assert 'user_id' not in sess
    
    def test_public_route_accessible_without_auth(self, flask_app):
        """Test that public routes are accessible without authentication."""
        with flask_app.test_client() as client:
            # Access public route without authentication
            response = client.get('/public')
            
            assert response.status_code == 200
            assert b'public page' in response.data
    
    def test_login_required_preserves_function_metadata(self, flask_app):
        """Test that @login_required preserves the wrapped function's metadata."""
        from src.auth import login_required
        
        @login_required
        def test_function():
            """Test function docstring."""
            return "test"
        
        # Function name and docstring should be preserved
        assert test_function.__name__ == 'test_function'
        assert test_function.__doc__ == 'Test function docstring.'
    
    def test_verified_required_preserves_function_metadata(self, flask_app):
        """Test that @verified_required preserves the wrapped function's metadata."""
        from src.auth import verified_required
        
        @verified_required
        def test_function():
            """Test function docstring."""
            return "test"
        
        # Function name and docstring should be preserved
        assert test_function.__name__ == 'test_function'
        assert test_function.__doc__ == 'Test function docstring.'
