"""
Booking module for Camargue Sailing website.

This module provides functions for managing sailing voyage bookings,
including calendar data retrieval and availability checking.

Requirements: 6.1, 6.2, 6.3
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_
from src.database import db_session
from src.models import Booking


def get_calendar_data(year: int) -> List[Dict[str, Any]]:
    """
    Fetch yearly planning data showing all bookings for a given year.
    
    This function retrieves all bookings for the specified year and returns
    them in a format suitable for calendar display. Each booking includes
    information about the date range and availability status.
    
    Args:
        year: The year for which to fetch calendar data
    
    Returns:
        A list of dictionaries, each representing a booking period with:
        - id: Booking ID
        - start_date: Start date of the booking
        - end_date: End date of the booking
        - status: Booking status ('confirmed', 'cancelled', etc.)
        - is_available: False (since these are booked periods)
    
    Requirements: 6.1, 6.2
    """
    # Define the date range for the year
    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)
    
    try:
        # Query all bookings that overlap with the specified year
        bookings = db_session.query(Booking).filter(
            and_(
                Booking.start_date <= end_of_year,
                Booking.end_date >= start_of_year
            )
        ).order_by(Booking.start_date).all()
        
        # Format bookings for calendar display
        calendar_data = []
        for booking in bookings:
            calendar_data.append({
                'id': booking.id,
                'start_date': booking.start_date.isoformat(),
                'end_date': booking.end_date.isoformat(),
                'status': booking.status,
                'is_available': False,
                'user_id': booking.user_id
            })
        
        return calendar_data
    except Exception as e:
        # Log database errors during calendar data retrieval
        import logging
        logging.error(f"Database error during calendar data retrieval for year {year}: {str(e)}")
        # Return empty list on error to allow page to render
        return []


def check_availability(start_date: date, end_date: date) -> bool:
    """
    Validate that a date range is available for booking.
    
    This function checks if the specified date range overlaps with any
    existing confirmed bookings. A period is considered available only
    if there are no overlapping bookings.
    
    Two date ranges overlap if:
    - The new booking starts before an existing booking ends, AND
    - The new booking ends after an existing booking starts
    
    Args:
        start_date: Start date of the requested booking period
        end_date: End date of the requested booking period
    
    Returns:
        True if the date range is available (no overlaps), False otherwise
    
    Requirements: 6.3, 7.3
    """
    # Validate input dates
    if end_date <= start_date:
        return False
    
    try:
        # Check for overlapping bookings
        # Two bookings overlap if:
        # (start1 < end2) AND (end1 > start2)
        overlapping_bookings = db_session.query(Booking).filter(
            and_(
                Booking.status == 'confirmed',
                Booking.start_date < end_date,
                Booking.end_date > start_date
            )
        ).count()
        
        return overlapping_bookings == 0
    except Exception as e:
        # Log database errors during availability check
        import logging
        logging.error(f"Database error during availability check: {str(e)}")
        # Return False on error to prevent booking (fail-safe)
        return False


def create_booking(user_id: int, start_date: date, end_date: date) -> Optional[Booking]:
    """
    Create a new booking for a user after validating date availability.

    This function validates that the requested date range is available
    (no overlapping bookings) and creates a new booking if valid. The
    booking is associated with the specified user and stored in the database.

    Validation checks:
    - Start date must not be in the past
    - End date must be after start date
    - Date range must not overlap with existing confirmed bookings

    Args:
        user_id: ID of the user making the booking
        start_date: Start date of the booking period
        end_date: End date of the booking period

    Returns:
        The created Booking object if successful, None if validation fails

    Raises:
        ValueError: If dates are invalid or period is already booked

    Requirements: 7.2, 7.3, 7.4, 7.5
    """
    # Get today's date for validation
    today = date.today()
    
    # Validate that start date is not in the past
    if start_date < today:
        raise ValueError("Start date cannot be in the past")
    
    # Validate date range
    if end_date <= start_date:
        raise ValueError("End date must be after start date")

    # Check for overlapping bookings
    if not check_availability(start_date, end_date):
        raise ValueError("The requested period is not available - it overlaps with an existing booking")

    # Create the booking
    booking = Booking(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        status='confirmed'
    )

    try:
        db_session.add(booking)
        db_session.commit()
        return booking
    except Exception as e:
        db_session.rollback()
        # Log the specific database error
        import logging
        logging.error(f"Database error during booking creation: {str(e)}")
        raise ValueError(f"Failed to create booking: {str(e)}")



def cancel_booking(booking_id: int, user_id: int) -> bool:
    """
    Cancel a booking with authorization check.

    This function cancels an existing booking after verifying that:
    1. The booking exists
    2. The user_id matches the booking's user_id (authorization)

    The booking status is updated to 'cancelled' rather than deleting
    the record, maintaining booking history.

    Args:
        booking_id: ID of the booking to cancel
        user_id: ID of the user requesting cancellation

    Returns:
        True if cancellation was successful, False if booking not found
        or user is not authorized

    Requirements: 7.5
    """
    # Fetch the booking
    booking = db_session.query(Booking).filter_by(id=booking_id).first()

    # Check if booking exists
    if not booking:
        return False

    # Check authorization - user must own the booking
    if booking.user_id != user_id:
        return False

    # Update booking status to cancelled
    booking.status = 'cancelled'

    try:
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        # Log database errors during booking cancellation
        import logging
        logging.error(f"Database error during booking cancellation (booking_id={booking_id}): {str(e)}")
        return False

