"""
Tests for the booking module.

This module contains unit tests for the booking calendar functions,
including get_calendar_data() and check_availability().

Requirements: 6.1, 6.2, 6.3, 7.3
"""

import pytest
from datetime import date, timedelta
from src.booking import get_calendar_data, check_availability, create_booking, cancel_booking
from src.models import User, Booking
from src.database import db_session, Base, engine


# Helper function to get future dates for testing
def future_date(days_from_now=30):
    """Get a date in the future for testing."""
    return date.today() + timedelta(days=days_from_now)


@pytest.fixture(scope='function')
def setup_database():
    """Create tables and clean up after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    db_session.rollback()
    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_database):
    """Create a test user for booking tests."""
    user = User(email='test@example.com', is_verified=True)
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


class TestGetCalendarData:
    """Tests for get_calendar_data() function."""
    
    def test_empty_calendar(self, setup_database):
        """Test calendar data for a year with no bookings."""
        calendar_data = get_calendar_data(2024)
        assert calendar_data == []
    
    def test_single_booking(self, test_user):
        """Test calendar data with a single booking."""
        # Create a booking
        booking = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 8),
            status='confirmed'
        )
        db_session.add(booking)
        db_session.commit()
        
        # Fetch calendar data
        calendar_data = get_calendar_data(2024)
        
        assert len(calendar_data) == 1
        assert calendar_data[0]['start_date'] == '2024-06-01'
        assert calendar_data[0]['end_date'] == '2024-06-08'
        assert calendar_data[0]['status'] == 'confirmed'
        assert calendar_data[0]['is_available'] is False
        assert calendar_data[0]['user_id'] == test_user.id
    
    def test_multiple_bookings(self, test_user):
        """Test calendar data with multiple bookings."""
        # Create multiple bookings
        bookings = [
            Booking(user_id=test_user.id, start_date=date(2024, 6, 1), 
                   end_date=date(2024, 6, 8), status='confirmed'),
            Booking(user_id=test_user.id, start_date=date(2024, 7, 15), 
                   end_date=date(2024, 7, 22), status='confirmed'),
            Booking(user_id=test_user.id, start_date=date(2024, 8, 10), 
                   end_date=date(2024, 8, 17), status='confirmed')
        ]
        for booking in bookings:
            db_session.add(booking)
        db_session.commit()
        
        # Fetch calendar data
        calendar_data = get_calendar_data(2024)
        
        assert len(calendar_data) == 3
        # Verify they are ordered by start_date
        assert calendar_data[0]['start_date'] == '2024-06-01'
        assert calendar_data[1]['start_date'] == '2024-07-15'
        assert calendar_data[2]['start_date'] == '2024-08-10'
    
    def test_booking_spanning_year_boundary(self, test_user):
        """Test calendar data with booking spanning year boundary."""
        # Create a booking that spans from 2023 to 2024
        booking = Booking(
            user_id=test_user.id,
            start_date=date(2023, 12, 28),
            end_date=date(2024, 1, 5),
            status='confirmed'
        )
        db_session.add(booking)
        db_session.commit()
        
        # Fetch calendar data for 2024
        calendar_data = get_calendar_data(2024)
        
        # Should include the booking since it overlaps with 2024
        assert len(calendar_data) == 1
        assert calendar_data[0]['start_date'] == '2023-12-28'
        assert calendar_data[0]['end_date'] == '2024-01-05'
    
    def test_different_booking_statuses(self, test_user):
        """Test calendar data includes bookings with different statuses."""
        # Create bookings with different statuses
        bookings = [
            Booking(user_id=test_user.id, start_date=date(2024, 6, 1), 
                   end_date=date(2024, 6, 8), status='confirmed'),
            Booking(user_id=test_user.id, start_date=date(2024, 7, 1), 
                   end_date=date(2024, 7, 8), status='cancelled')
        ]
        for booking in bookings:
            db_session.add(booking)
        db_session.commit()
        
        # Fetch calendar data
        calendar_data = get_calendar_data(2024)
        
        assert len(calendar_data) == 2
        assert calendar_data[0]['status'] == 'confirmed'
        assert calendar_data[1]['status'] == 'cancelled'


class TestCheckAvailability:
    """Tests for check_availability() function."""
    
    def test_available_period_no_bookings(self, setup_database):
        """Test availability check when there are no bookings."""
        start = date(2024, 6, 1)
        end = date(2024, 6, 8)
        
        assert check_availability(start, end) is True
    
    def test_invalid_date_range(self, setup_database):
        """Test availability check with end date before start date."""
        start = date(2024, 6, 8)
        end = date(2024, 6, 1)
        
        assert check_availability(start, end) is False
    
    def test_same_start_and_end_date(self, setup_database):
        """Test availability check with same start and end date."""
        start = date(2024, 6, 1)
        end = date(2024, 6, 1)
        
        assert check_availability(start, end) is False
    
    def test_overlapping_booking_complete_overlap(self, test_user):
        """Test availability when new booking completely overlaps existing."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 8),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book the same period
        assert check_availability(date(2024, 6, 1), date(2024, 6, 8)) is False
    
    def test_overlapping_booking_partial_overlap_start(self, test_user):
        """Test availability when new booking overlaps at the start."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 5),
            end_date=date(2024, 6, 12),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period that overlaps at the start
        assert check_availability(date(2024, 6, 1), date(2024, 6, 8)) is False
    
    def test_overlapping_booking_partial_overlap_end(self, test_user):
        """Test availability when new booking overlaps at the end."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 8),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period that overlaps at the end
        assert check_availability(date(2024, 6, 5), date(2024, 6, 12)) is False
    
    def test_overlapping_booking_contained_within(self, test_user):
        """Test availability when new booking is contained within existing."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 15),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period contained within existing
        assert check_availability(date(2024, 6, 5), date(2024, 6, 10)) is False
    
    def test_overlapping_booking_contains_existing(self, test_user):
        """Test availability when new booking contains existing booking."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 5),
            end_date=date(2024, 6, 10),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period that contains existing
        assert check_availability(date(2024, 6, 1), date(2024, 6, 15)) is False
    
    def test_non_overlapping_booking_before(self, test_user):
        """Test availability when new booking is before existing booking."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 10),
            end_date=date(2024, 6, 17),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period before existing
        assert check_availability(date(2024, 6, 1), date(2024, 6, 8)) is True
    
    def test_non_overlapping_booking_after(self, test_user):
        """Test availability when new booking is after existing booking."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 8),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period after existing
        assert check_availability(date(2024, 6, 10), date(2024, 6, 17)) is True
    
    def test_adjacent_bookings_end_to_start(self, test_user):
        """Test availability when bookings are adjacent (end date = start date)."""
        # Create existing booking
        existing = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 8),
            status='confirmed'
        )
        db_session.add(existing)
        db_session.commit()
        
        # Try to book period starting on existing end date
        # This should be available since end_date is exclusive
        assert check_availability(date(2024, 6, 8), date(2024, 6, 15)) is True
    
    def test_cancelled_booking_does_not_block(self, test_user):
        """Test that cancelled bookings don't block availability."""
        # Create cancelled booking
        cancelled = Booking(
            user_id=test_user.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 8),
            status='cancelled'
        )
        db_session.add(cancelled)
        db_session.commit()
        
        # Try to book the same period - should be available
        assert check_availability(date(2024, 6, 1), date(2024, 6, 8)) is True
    
    def test_multiple_non_overlapping_bookings(self, test_user):
        """Test availability with multiple non-overlapping bookings."""
        # Create multiple bookings
        bookings = [
            Booking(user_id=test_user.id, start_date=date(2024, 6, 1), 
                   end_date=date(2024, 6, 8), status='confirmed'),
            Booking(user_id=test_user.id, start_date=date(2024, 7, 1), 
                   end_date=date(2024, 7, 8), status='confirmed')
        ]
        for booking in bookings:
            db_session.add(booking)
        db_session.commit()
        
        # Try to book period between existing bookings
        assert check_availability(date(2024, 6, 15), date(2024, 6, 22)) is True



class TestCreateBooking:
    """Tests for create_booking() function."""

    def test_create_booking_success(self, test_user):
        """Test successful booking creation."""
        from src.booking import create_booking

        start = future_date(30)
        end = future_date(37)

        booking = create_booking(test_user.id, start, end)

        assert booking is not None
        assert booking.user_id == test_user.id
        assert booking.start_date == start
        assert booking.end_date == end
        assert booking.status == 'confirmed'
        assert booking.id is not None  # Should have been assigned by database

    def test_create_booking_invalid_date_range(self, test_user):
        """Test booking creation with end date before start date."""
        from src.booking import create_booking

        start = future_date(37)
        end = future_date(30)

        with pytest.raises(ValueError, match="End date must be after start date"):
            create_booking(test_user.id, start, end)

    def test_create_booking_same_dates(self, test_user):
        """Test booking creation with same start and end date."""
        from src.booking import create_booking

        start = future_date(30)
        end = future_date(30)

        with pytest.raises(ValueError, match="End date must be after start date"):
            create_booking(test_user.id, start, end)

    def test_create_booking_overlapping_existing(self, test_user):
        """Test booking creation when period overlaps with existing booking."""
        from src.booking import create_booking

        # Create first booking
        first_booking = create_booking(test_user.id, future_date(30), future_date(37))
        assert first_booking is not None

        # Try to create overlapping booking
        with pytest.raises(ValueError, match="not available.*overlaps"):
            create_booking(test_user.id, future_date(34), future_date(41))

    def test_create_booking_non_overlapping(self, test_user):
        """Test creating multiple non-overlapping bookings."""
        from src.booking import create_booking

        # Create first booking
        first_booking = create_booking(test_user.id, future_date(30), future_date(37))
        assert first_booking is not None

        # Create second non-overlapping booking
        second_booking = create_booking(test_user.id, future_date(44), future_date(51))
        assert second_booking is not None

        # Verify both bookings exist
        assert first_booking.id != second_booking.id

    def test_create_booking_adjacent_periods(self, test_user):
        """Test creating bookings in adjacent periods (end-to-start)."""
        from src.booking import create_booking

        # Create first booking
        first_booking = create_booking(test_user.id, future_date(30), future_date(37))
        assert first_booking is not None

        # Create adjacent booking (starts on previous end date)
        second_booking = create_booking(test_user.id, future_date(37), future_date(44))
        assert second_booking is not None

    def test_create_booking_persists_to_database(self, test_user):
        """Test that created booking is persisted to database."""
        from src.booking import create_booking

        start = future_date(30)
        end = future_date(37)

        booking = create_booking(test_user.id, start, end)
        booking_id = booking.id

        # Clear session and query again to verify persistence
        db_session.expire_all()

        retrieved_booking = db_session.query(Booking).filter_by(id=booking_id).first()
        assert retrieved_booking is not None
        assert retrieved_booking.user_id == test_user.id
        assert retrieved_booking.start_date == start
        assert retrieved_booking.end_date == end

    def test_create_booking_multiple_users(self, test_user, setup_database):
        """Test that different users cannot book overlapping periods."""
        from src.booking import create_booking

        # Create second user
        user2 = User(email='user2@example.com', is_verified=True)
        user2.set_password('password123')
        db_session.add(user2)
        db_session.commit()

        # First user creates booking
        first_booking = create_booking(test_user.id, future_date(30), future_date(37))
        assert first_booking is not None

        # Second user tries to book overlapping period - should fail
        with pytest.raises(ValueError, match="not available.*overlaps"):
            create_booking(user2.id, future_date(34), future_date(41))




class TestCancelBooking:
    """Tests for cancel_booking() function."""

    def test_cancel_booking_success(self, test_user):
        """Test successful booking cancellation."""
        from src.booking import create_booking, cancel_booking

        # Create a booking
        booking = create_booking(test_user.id, future_date(30), future_date(37))
        booking_id = booking.id

        # Cancel the booking
        result = cancel_booking(booking_id, test_user.id)

        assert result is True

        # Verify booking status is cancelled
        db_session.expire_all()
        cancelled_booking = db_session.query(Booking).filter_by(id=booking_id).first()
        assert cancelled_booking.status == 'cancelled'

    def test_cancel_booking_nonexistent(self, test_user):
        """Test cancelling a booking that doesn't exist."""
        from src.booking import cancel_booking

        # Try to cancel non-existent booking
        result = cancel_booking(99999, test_user.id)

        assert result is False

    def test_cancel_booking_unauthorized(self, test_user, setup_database):
        """Test cancelling a booking by a different user."""
        from src.booking import create_booking, cancel_booking

        # Create second user
        user2 = User(email='user2@example.com', is_verified=True)
        user2.set_password('password123')
        db_session.add(user2)
        db_session.commit()

        # First user creates booking
        booking = create_booking(test_user.id, future_date(30), future_date(37))
        booking_id = booking.id

        # Second user tries to cancel first user's booking
        result = cancel_booking(booking_id, user2.id)

        assert result is False

        # Verify booking is still confirmed
        db_session.expire_all()
        unchanged_booking = db_session.query(Booking).filter_by(id=booking_id).first()
        assert unchanged_booking.status == 'confirmed'

    def test_cancel_booking_makes_period_available(self, test_user):
        """Test that cancelling a booking makes the period available again."""
        from src.booking import create_booking, cancel_booking, check_availability

        # Create a booking
        start = future_date(30)
        end = future_date(37)
        booking = create_booking(test_user.id, start, end)
        booking_id = booking.id

        # Verify period is not available
        assert check_availability(start, end) is False

        # Cancel the booking
        result = cancel_booking(booking_id, test_user.id)
        assert result is True

        # Verify period is now available
        assert check_availability(start, end) is True

    def test_cancel_already_cancelled_booking(self, test_user):
        """Test cancelling a booking that is already cancelled."""
        from src.booking import create_booking, cancel_booking

        # Create and cancel a booking
        booking = create_booking(test_user.id, future_date(30), future_date(37))
        booking_id = booking.id
        cancel_booking(booking_id, test_user.id)

        # Try to cancel again
        result = cancel_booking(booking_id, test_user.id)

        # Should still return True (idempotent operation)
        assert result is True

        # Verify status is still cancelled
        db_session.expire_all()
        cancelled_booking = db_session.query(Booking).filter_by(id=booking_id).first()
        assert cancelled_booking.status == 'cancelled'

