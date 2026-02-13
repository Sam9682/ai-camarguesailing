"""
Email service module for Camargue Sailing website.

This module provides email sending functionality using Flask-Mail.
It handles SMTP configuration from environment variables and provides
a simple interface for sending emails.

Requirements: 10.1, 10.5
"""

from flask import Flask
from flask_mail import Mail, Message
from typing import Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global mail instance
mail = None


def init_mail(app: Flask) -> None:
    """
    Initialize Flask-Mail with the Flask application.
    
    Args:
        app: Flask application instance with mail configuration
    """
    global mail
    mail = Mail(app)
    logger.info("Flask-Mail initialized successfully")


def send_email(to: str, subject: str, body: str, html: Optional[str] = None, max_retries: int = 3) -> bool:
    """
    Send an email using Flask-Mail with retry logic and exponential backoff.
    
    This function sends an email to the specified recipient with the given
    subject and body. It uses SMTP settings configured in the Flask app
    via environment variables. If sending fails, it will retry up to max_retries
    times with exponential backoff.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Plain text email body
        html: Optional HTML email body
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    
    Raises:
        ValueError: If mail is not initialized
    
    Requirements: 10.1, 10.4, 10.5
    """
    if mail is None:
        logger.error("Flask-Mail not initialized. Call init_mail() first.")
        raise ValueError("Flask-Mail not initialized. Call init_mail() first.")
    
    attempt = 0
    last_exception = None
    
    while attempt < max_retries:
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html
            )
            
            mail.send(msg)
            
            if attempt > 0:
                logger.info(f"Email sent successfully to {to} after {attempt + 1} attempt(s)")
            else:
                logger.info(f"Email sent successfully to {to}")
            
            return True
            
        except Exception as e:
            attempt += 1
            last_exception = e
            
            # Log the failure with details
            logger.error(
                f"Failed to send email to {to} (attempt {attempt}/{max_retries}): "
                f"{type(e).__name__}: {str(e)}"
            )
            
            # If we haven't exhausted retries, wait with exponential backoff
            if attempt < max_retries:
                # Exponential backoff: 2^(attempt-1) seconds (1s, 2s, 4s, ...)
                backoff_time = 2 ** (attempt - 1)
                logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
    
    # All retries exhausted
    logger.error(
        f"Failed to send email to {to} after {max_retries} attempts. "
        f"Last error: {type(last_exception).__name__}: {str(last_exception)}"
    )
    
    return False


def send_verification_email(user, base_url: str) -> bool:
    """
    Send a verification email to a newly registered user.
    
    This function generates a unique verification token for the user and sends
    an email containing a verification link. The link directs the user to a
    verification endpoint where their email will be confirmed.
    
    Args:
        user: User object (must have id and email attributes)
        base_url: Base URL of the application (e.g., 'http://localhost:5000')
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    
    Requirements: 3.1, 3.2, 10.2
    """
    from src.auth import generate_verification_token
    
    try:
        # Generate unique verification token
        token = generate_verification_token(user.id)
        
        # Build verification URL
        verification_url = f"{base_url}/verify/{token}"
        
        # Email subject
        subject = "Verify Your Email - Camargue Sailing"
        
        # Plain text email body
        body = f"""Welcome to Camargue Sailing!

Thank you for registering with us. To complete your registration and access all features, please verify your email address by clicking the link below:

{verification_url}

This verification link will expire in 24 hours.

If you did not create an account with Camargue Sailing, please ignore this email.

Best regards,
The Camargue Sailing Team
"""
        
        # HTML email body
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #0066cc;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .footer {{
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Camargue Sailing!</h1>
        </div>
        <div class="content">
            <p>Thank you for registering with us. To complete your registration and access all features, please verify your email address by clicking the button below:</p>
            
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all;">{verification_url}</p>
            
            <p><strong>This verification link will expire in 24 hours.</strong></p>
            
            <p>If you did not create an account with Camargue Sailing, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Camargue Sailing Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Send the email
        success = send_email(user.email, subject, body, html)
        
        if success:
            logger.info(f"Verification email sent to {user.email} with token {token[:8]}...")
        else:
            logger.error(f"Failed to send verification email to {user.email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {str(e)}")
        return False


def send_booking_confirmation(booking, user) -> bool:
    """
    Send a booking confirmation email to a user.
    
    This function sends a confirmation email containing the booking details
    and voyage information after a successful booking is created.
    
    Args:
        booking: Booking object (must have id, start_date, end_date, status attributes)
        user: User object (must have email attribute)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    
    Requirements: 7.6, 10.3
    """
    try:
        # Format dates for display
        start_date_str = booking.start_date.strftime("%B %d, %Y")
        end_date_str = booking.end_date.strftime("%B %d, %Y")
        
        # Calculate duration
        duration = (booking.end_date - booking.start_date).days
        
        # Email subject
        subject = "Booking Confirmation - Camargue Sailing"
        
        # Plain text email body
        body = f"""Booking Confirmation

Dear Sailor,

Thank you for booking your sailing voyage with Camargue Sailing! We are excited to have you join us for an unforgettable week in the beautiful Camargue region.

BOOKING DETAILS:
-----------------
Booking Reference: #{booking.id}
Start Date: {start_date_str}
End Date: {end_date_str}
Duration: {duration} days
Status: {booking.status.capitalize()}

VOYAGE INFORMATION:
-------------------
Your one-week sailing voyage will take place in the stunning waters of the South of France, departing from Saintes-Maries-de-la-Mer in the heart of the Camargue. You'll experience the beauty of the Mediterranean aboard our AMEL sailing yacht.

WHAT TO BRING:
- Comfortable sailing attire
- Sun protection (hat, sunglasses, sunscreen)
- Light jacket for evening breezes
- Personal items and medications

NEXT STEPS:
We will send you additional information about meeting points, what to expect, and detailed itinerary closer to your departure date.

If you have any questions or need to make changes to your booking, please contact us.

We look forward to sailing with you!

Best regards,
The Camargue Sailing Team
"""
        
        # HTML email body
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #0066cc;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .booking-details {{
            background-color: white;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #0066cc;
        }}
        .booking-details h3 {{
            margin-top: 0;
            color: #0066cc;
        }}
        .detail-row {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .detail-label {{
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }}
        .voyage-info {{
            background-color: #e6f2ff;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .footer {{
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        ul {{
            margin: 10px 0;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Booking Confirmation</h1>
        </div>
        <div class="content">
            <p>Dear Sailor,</p>
            
            <p>Thank you for booking your sailing voyage with Camargue Sailing! We are excited to have you join us for an unforgettable week in the beautiful Camargue region.</p>
            
            <div class="booking-details">
                <h3>Booking Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Booking Reference:</span>
                    <span>#{booking.id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Start Date:</span>
                    <span>{start_date_str}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">End Date:</span>
                    <span>{end_date_str}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration:</span>
                    <span>{duration} days</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span>{booking.status.capitalize()}</span>
                </div>
            </div>
            
            <div class="voyage-info">
                <h3>Voyage Information</h3>
                <p>Your one-week sailing voyage will take place in the stunning waters of the South of France, departing from <strong>Saintes-Maries-de-la-Mer</strong> in the heart of the Camargue. You'll experience the beauty of the Mediterranean aboard our AMEL sailing yacht.</p>
            </div>
            
            <h3>What to Bring:</h3>
            <ul>
                <li>Comfortable sailing attire</li>
                <li>Sun protection (hat, sunglasses, sunscreen)</li>
                <li>Light jacket for evening breezes</li>
                <li>Personal items and medications</li>
            </ul>
            
            <h3>Next Steps:</h3>
            <p>We will send you additional information about meeting points, what to expect, and detailed itinerary closer to your departure date.</p>
            
            <p>If you have any questions or need to make changes to your booking, please contact us.</p>
            
            <p><strong>We look forward to sailing with you!</strong></p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Camargue Sailing Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Send the email
        success = send_email(user.email, subject, body, html)
        
        if success:
            logger.info(f"Booking confirmation email sent to {user.email} for booking #{booking.id}")
        else:
            logger.error(f"Failed to send booking confirmation email to {user.email} for booking #{booking.id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {str(e)}")
        return False
