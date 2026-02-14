"""
Tests for database error handling across the application.

This test module verifies that database operations properly handle:
- Connection failures
- Constraint violations (IntegrityError)
- Transaction rollback
- General database errors

Requirements: 12.3
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError
from datetime import date, datetime

from src.auth import (
    register_user, 
    RegistrationError, 
    generate_verification_token,
    verify_token,
    get_user_by_id
)
from src.booking import (
    create_booking,
    cancel_booking,
    check_availability,
    get_calendar_data
)
from src.forum import (
    create_post,
    create_reply,
    get_all_posts
)
from src.models import User, Booking, ForumPost
from src.database import db_session, Base, engine


@pytest.fixture(scope='function')
def setup_database():
    """Set up a clean database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean up after test
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


class TestAuthErrorHandling:
    """Test error handling in authentication module."""
    
    def test_register_user_handles_integrity_error(self, setup_database):
        """Test that duplicate email registration handles IntegrityError properly."""
        # Create a user first
        user1 = register_user("test@example.com", "password123")
        assert user1 is not None
        
        # Try to register with the same email - should raise RegistrationError
        with pytest.raises(RegistrationError, match="already registered"):
            register_user("test@example.com", "password456")
    
    def test_register_user_handles_database_error(self, setup_database):
        """Test that registration handles general database errors."""
        with patch('src.auth.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            with pytest.raises(RegistrationError, match="Failed to create user account"):
                register_user("test@example.com", "password123")
    
    def test_generate_verification_token_handles_database_error(self, setup_database):
        """Test that token generation handles database errors."""
        # Create a user first
        user = register_user("test@example.com", "password123")
        
        # Mock commit to raise an exception
        with patch('src.auth.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            with pytest.raises(ValueError, match="Failed to generate verification token"):
                generate_verification_token(user.id)
    
    def test_verify_token_handles_database_error(self, setup_database):
        """Test that token verification handles database errors."""
        # Create a user and token
        user = register_user("test@example.com", "password123")
        token = generate_verification_token(user.id)
        
        # Mock commit to raise an exception
        with patch('src.auth.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            with pytest.raises(ValueError, match="Failed to verify user"):
                verify_token(token)
    
    def test_get_user_by_id_handles_database_error(self, setup_database):
        """Test that user lookup handles database errors gracefully."""
        with patch('src.auth.db_session.query', side_effect=OperationalError("statement", "params", "orig")):
            result = get_user_by_id(1)
            assert result is None  # Should return None on error


class TestBookingErrorHandling:
    """Test error handling in booking module."""
    
    def test_create_booking_handles_database_error(self, setup_database):
        """Test that booking creation handles database errors."""
        from datetime import timedelta
        # Create a user first
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        # Use future dates
        future_start = date.today() + timedelta(days=30)
        future_end = future_start + timedelta(days=7)
        
        # Mock commit to raise an exception
        with patch('src.booking.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            with pytest.raises(ValueError, match="Failed to create booking"):
                create_booking(user.id, future_start, future_end)
    
    def test_check_availability_handles_database_error(self, setup_database):
        """Test that availability check handles database errors gracefully."""
        from datetime import timedelta
        future_start = date.today() + timedelta(days=30)
        future_end = future_start + timedelta(days=7)
        
        with patch('src.booking.db_session.query', side_effect=OperationalError("statement", "params", "orig")):
            # Should return False on error (fail-safe)
            result = check_availability(future_start, future_end)
            assert result is False
    
    def test_get_calendar_data_handles_database_error(self, setup_database):
        """Test that calendar data retrieval handles database errors gracefully."""
        with patch('src.booking.db_session.query', side_effect=OperationalError("statement", "params", "orig")):
            # Should return empty list on error
            result = get_calendar_data(2024)
            assert result == []
    
    def test_cancel_booking_handles_database_error(self, setup_database):
        """Test that booking cancellation handles database errors."""
        from datetime import timedelta
        # Create a user and booking first
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        # Use future dates
        future_start = date.today() + timedelta(days=30)
        future_end = future_start + timedelta(days=7)
        
        booking = create_booking(user.id, future_start, future_end)
        
        # Mock commit to raise an exception
        with patch('src.booking.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            result = cancel_booking(booking.id, user.id)
            assert result is False  # Should return False on error


class TestForumErrorHandling:
    """Test error handling in forum module."""
    
    def test_create_post_handles_database_error(self, setup_database):
        """Test that post creation handles database errors."""
        # Create a user first
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        # Mock commit to raise an exception
        with patch('src.forum.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            with pytest.raises(ValueError, match="Failed to create forum post"):
                create_post(user.id, "Test Title", "Test content")
    
    def test_create_reply_handles_database_error(self, setup_database):
        """Test that reply creation handles database errors."""
        # Create a user and post first
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        post = create_post(user.id, "Test Title", "Test content")
        
        # Mock commit to raise an exception
        with patch('src.forum.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            with pytest.raises(ValueError, match="Failed to create reply"):
                create_reply(post.id, user.id, "Test reply")
    
    def test_get_all_posts_handles_database_error(self, setup_database):
        """Test that post retrieval handles database errors gracefully."""
        with patch('src.forum.db_session.query', side_effect=OperationalError("statement", "params", "orig")):
            # Should return empty list on error
            result = get_all_posts()
            assert result == []


class TestTransactionRollback:
    """Test that database transactions are properly rolled back on errors."""
    
    def test_registration_rollback_on_error(self, setup_database):
        """Test that failed registration rolls back the transaction."""
        initial_count = db_session.query(User).count()
        
        # Try to register with invalid data that will cause an error
        with patch('src.auth.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            try:
                register_user("test@example.com", "password123")
            except RegistrationError:
                pass
        
        # Verify no user was added
        final_count = db_session.query(User).count()
        assert final_count == initial_count
    
    def test_booking_rollback_on_error(self, setup_database):
        """Test that failed booking creation rolls back the transaction."""
        from datetime import timedelta
        # Create a user first
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        initial_count = db_session.query(Booking).count()
        
        # Use future dates
        future_start = date.today() + timedelta(days=30)
        future_end = future_start + timedelta(days=7)
        
        # Try to create a booking that will fail
        with patch('src.booking.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            try:
                create_booking(user.id, future_start, future_end)
            except ValueError:
                pass
        
        # Verify no booking was added
        final_count = db_session.query(Booking).count()
        assert final_count == initial_count
    
    def test_forum_post_rollback_on_error(self, setup_database):
        """Test that failed post creation rolls back the transaction."""
        # Create a user first
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        initial_count = db_session.query(ForumPost).count()
        
        # Try to create a post that will fail
        with patch('src.forum.db_session.commit', side_effect=DatabaseError("statement", "params", "orig")):
            try:
                create_post(user.id, "Test Title", "Test content")
            except ValueError:
                pass
        
        # Verify no post was added
        final_count = db_session.query(ForumPost).count()
        assert final_count == initial_count


class TestConstraintViolations:
    """Test handling of database constraint violations."""
    
    def test_unique_email_constraint(self, setup_database):
        """Test that unique email constraint is properly handled."""
        # Create first user
        user1 = register_user("test@example.com", "password123")
        assert user1 is not None
        
        # Try to create second user with same email
        with pytest.raises(RegistrationError, match="already registered"):
            register_user("test@example.com", "password456")
    
    def test_booking_date_validation(self, setup_database):
        """Test that booking date constraints are validated."""
        from datetime import timedelta
        # Create a user
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        # Use future dates but with end before start
        future_start = date.today() + timedelta(days=30)
        future_end = future_start - timedelta(days=7)
        
        # Try to create booking with end_date before start_date
        with pytest.raises(ValueError, match="End date must be after start date"):
            create_booking(user.id, future_start, future_end)
    
    def test_overlapping_booking_constraint(self, setup_database):
        """Test that overlapping bookings are prevented."""
        from datetime import timedelta
        # Create a user
        user = register_user("test@example.com", "password123")
        user.is_verified = True
        db_session.commit()
        
        # Use future dates
        future_start = date.today() + timedelta(days=30)
        future_end = future_start + timedelta(days=7)
        
        # Create first booking
        booking1 = create_booking(user.id, future_start, future_end)
        assert booking1 is not None
        
        # Try to create overlapping booking
        overlap_start = future_start + timedelta(days=3)
        overlap_end = future_end + timedelta(days=3)
        
        with pytest.raises(ValueError, match="not available"):
            create_booking(user.id, overlap_start, overlap_end)
