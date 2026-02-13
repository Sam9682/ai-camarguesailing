"""
Unit tests for email service module.

Tests the email sending functionality with mocked SMTP.
"""

import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from src.email_service import init_mail, send_email, send_verification_email


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MAIL_SERVER'] = 'smtp.test.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'test@example.com'
    app.config['MAIL_PASSWORD'] = 'testpassword'
    app.config['MAIL_DEFAULT_SENDER'] = 'test@example.com'
    return app


@pytest.fixture
def mock_user():
    """Create a mock user object for testing."""
    user = MagicMock()
    user.id = 1
    user.email = "testuser@example.com"
    return user


def test_init_mail(app):
    """Test that Flask-Mail initializes correctly."""
    init_mail(app)
    # If no exception is raised, initialization succeeded
    assert True


def test_send_email_not_initialized():
    """Test that send_email raises error when mail not initialized."""
    # Reset mail to None
    import src.email_service
    src.email_service.mail = None
    
    with pytest.raises(ValueError, match="Flask-Mail not initialized"):
        send_email("test@example.com", "Test", "Test body")


@patch('src.email_service.mail')
def test_send_email_success(mock_mail, app):
    """Test successful email sending."""
    init_mail(app)
    
    # Mock the mail.send method
    mock_mail.send = MagicMock()
    
    result = send_email(
        to="recipient@example.com",
        subject="Test Subject",
        body="Test body content"
    )
    
    assert result is True


@patch('src.email_service.mail')
def test_send_email_with_html(mock_mail, app):
    """Test email sending with HTML content."""
    init_mail(app)
    
    # Mock the mail.send method
    mock_mail.send = MagicMock()
    
    result = send_email(
        to="recipient@example.com",
        subject="Test Subject",
        body="Test body content",
        html="<p>Test HTML content</p>"
    )
    
    assert result is True


def test_send_email_failure(app):
    """Test email sending failure handling."""
    init_mail(app)
    
    # Mock the mail.send method to raise an exception
    with patch('src.email_service.mail.send', side_effect=Exception("SMTP error")):
        result = send_email(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body content"
        )
        
        assert result is False


@patch('src.auth.generate_verification_token')
def test_send_verification_email_success(mock_generate_token, app, mock_user):
    """Test successful verification email sending."""
    init_mail(app)
    
    # Mock token generation
    mock_generate_token.return_value = "test_token_12345"
    
    # Mock the mail.send method
    with patch('src.email_service.mail.send') as mock_send:
        result = send_verification_email(mock_user, "http://localhost:5000")
        
        assert result is True
        mock_generate_token.assert_called_once_with(mock_user.id)
        mock_send.assert_called_once()


@patch('src.auth.generate_verification_token')
def test_send_verification_email_contains_token(mock_generate_token, app, mock_user):
    """Test that verification email contains the verification link."""
    init_mail(app)
    
    # Mock token generation
    test_token = "unique_test_token_abc123"
    mock_generate_token.return_value = test_token
    
    # Capture the message being sent
    sent_messages = []
    def capture_send(msg):
        sent_messages.append(msg)
    
    with patch('src.email_service.mail.send', side_effect=capture_send):
        result = send_verification_email(mock_user, "http://localhost:5000")
        
        assert result is True
        assert len(sent_messages) == 1
        
        # Check that the verification URL is in both body and HTML
        expected_url = f"http://localhost:5000/verify/{test_token}"
        assert expected_url in sent_messages[0].body
        assert expected_url in sent_messages[0].html


@patch('src.auth.generate_verification_token')
def test_send_verification_email_correct_recipient(mock_generate_token, app, mock_user):
    """Test that verification email is sent to the correct recipient."""
    init_mail(app)
    
    # Mock token generation
    mock_generate_token.return_value = "test_token"
    
    # Capture the message being sent
    sent_messages = []
    def capture_send(msg):
        sent_messages.append(msg)
    
    with patch('src.email_service.mail.send', side_effect=capture_send):
        result = send_verification_email(mock_user, "http://localhost:5000")
        
        assert result is True
        assert len(sent_messages) == 1
        assert sent_messages[0].recipients == [mock_user.email]


@patch('src.auth.generate_verification_token')
def test_send_verification_email_failure(mock_generate_token, app, mock_user):
    """Test verification email sending failure handling."""
    init_mail(app)
    
    # Mock token generation
    mock_generate_token.return_value = "test_token"
    
    # Mock the mail.send method to raise an exception
    with patch('src.email_service.mail.send', side_effect=Exception("SMTP error")):
        result = send_verification_email(mock_user, "http://localhost:5000")
        
        assert result is False


@patch('src.auth.generate_verification_token')
def test_send_verification_email_token_generation_failure(mock_generate_token, app, mock_user):
    """Test verification email when token generation fails."""
    init_mail(app)
    
    # Mock token generation to raise an exception
    mock_generate_token.side_effect = ValueError("Token generation failed")
    
    result = send_verification_email(mock_user, "http://localhost:5000")
    
    assert result is False



@pytest.fixture
def mock_booking():
    """Create a mock booking object for testing."""
    from datetime import date
    booking = MagicMock()
    booking.id = 42
    booking.start_date = date(2024, 7, 1)
    booking.end_date = date(2024, 7, 8)
    booking.status = 'confirmed'
    return booking


def test_send_booking_confirmation_success(app, mock_user, mock_booking):
    """Test successful booking confirmation email sending."""
    from src.email_service import send_booking_confirmation
    
    init_mail(app)
    
    # Mock the mail.send method
    with patch('src.email_service.mail.send') as mock_send:
        result = send_booking_confirmation(mock_booking, mock_user)
        
        assert result is True
        mock_send.assert_called_once()


def test_send_booking_confirmation_contains_booking_details(app, mock_user, mock_booking):
    """Test that booking confirmation email contains booking details."""
    from src.email_service import send_booking_confirmation
    
    init_mail(app)
    
    # Capture the message being sent
    sent_messages = []
    def capture_send(msg):
        sent_messages.append(msg)
    
    with patch('src.email_service.mail.send', side_effect=capture_send):
        result = send_booking_confirmation(mock_booking, mock_user)
        
        assert result is True
        assert len(sent_messages) == 1
        
        # Check that booking details are in both body and HTML
        message = sent_messages[0]
        
        # Check booking reference
        assert f"#{mock_booking.id}" in message.body
        assert f"#{mock_booking.id}" in message.html
        
        # Check dates are formatted and present
        assert "July 01, 2024" in message.body
        assert "July 08, 2024" in message.body
        assert "July 01, 2024" in message.html
        assert "July 08, 2024" in message.html
        
        # Check duration (7 days)
        assert "7 days" in message.body
        assert "7 days" in message.html
        
        # Check status
        assert "Confirmed" in message.body
        assert "Confirmed" in message.html


def test_send_booking_confirmation_contains_voyage_info(app, mock_user, mock_booking):
    """Test that booking confirmation email contains voyage information."""
    from src.email_service import send_booking_confirmation
    
    init_mail(app)
    
    # Capture the message being sent
    sent_messages = []
    def capture_send(msg):
        sent_messages.append(msg)
    
    with patch('src.email_service.mail.send', side_effect=capture_send):
        result = send_booking_confirmation(mock_booking, mock_user)
        
        assert result is True
        assert len(sent_messages) == 1
        
        message = sent_messages[0]
        
        # Check voyage information is present
        assert "Saintes-Maries-de-la-Mer" in message.body
        assert "Camargue" in message.body
        assert "AMEL" in message.body
        
        assert "Saintes-Maries-de-la-Mer" in message.html
        assert "Camargue" in message.html
        assert "AMEL" in message.html


def test_send_booking_confirmation_correct_recipient(app, mock_user, mock_booking):
    """Test that booking confirmation email is sent to the correct recipient."""
    from src.email_service import send_booking_confirmation
    
    init_mail(app)
    
    # Capture the message being sent
    sent_messages = []
    def capture_send(msg):
        sent_messages.append(msg)
    
    with patch('src.email_service.mail.send', side_effect=capture_send):
        result = send_booking_confirmation(mock_booking, mock_user)
        
        assert result is True
        assert len(sent_messages) == 1
        assert sent_messages[0].recipients == [mock_user.email]


def test_send_booking_confirmation_failure(app, mock_user, mock_booking):
    """Test booking confirmation email sending failure handling."""
    from src.email_service import send_booking_confirmation
    
    init_mail(app)
    
    # Mock the mail.send method to raise an exception
    with patch('src.email_service.mail.send', side_effect=Exception("SMTP error")):
        result = send_booking_confirmation(mock_booking, mock_user)
        
        assert result is False


def test_send_booking_confirmation_exception_handling(app, mock_user):
    """Test booking confirmation email handles exceptions gracefully."""
    from src.email_service import send_booking_confirmation
    
    init_mail(app)
    
    # Create a booking with invalid date to trigger exception
    invalid_booking = MagicMock()
    invalid_booking.start_date = None  # This will cause an AttributeError
    
    result = send_booking_confirmation(invalid_booking, mock_user)
    
    assert result is False


# Tests for retry logic and exponential backoff (Task 4.4)

def test_send_email_retry_success_on_second_attempt(app):
    """Test that email sending succeeds on retry after initial failure."""
    init_mail(app)
    
    # Mock the mail.send method to fail once, then succeed
    call_count = 0
    def mock_send_with_retry(msg):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Temporary SMTP error")
        # Second call succeeds (no exception)
    
    with patch('src.email_service.mail.send', side_effect=mock_send_with_retry):
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = send_email(
                to="recipient@example.com",
                subject="Test Subject",
                body="Test body content"
            )
            
            assert result is True
            assert call_count == 2


def test_send_email_retry_exhausted(app):
    """Test that email sending fails after exhausting all retries."""
    init_mail(app)
    
    # Mock the mail.send method to always fail
    call_count = 0
    def mock_send_always_fail(msg):
        nonlocal call_count
        call_count += 1
        raise Exception("Persistent SMTP error")
    
    with patch('src.email_service.mail.send', side_effect=mock_send_always_fail):
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = send_email(
                to="recipient@example.com",
                subject="Test Subject",
                body="Test body content",
                max_retries=3
            )
            
            assert result is False
            assert call_count == 3


def test_send_email_exponential_backoff(app):
    """Test that exponential backoff is applied between retries."""
    init_mail(app)
    
    # Mock the mail.send method to always fail
    def mock_send_always_fail(msg):
        raise Exception("SMTP error")
    
    sleep_times = []
    def mock_sleep(seconds):
        sleep_times.append(seconds)
    
    with patch('src.email_service.mail.send', side_effect=mock_send_always_fail):
        with patch('time.sleep', side_effect=mock_sleep):
            result = send_email(
                to="recipient@example.com",
                subject="Test Subject",
                body="Test body content",
                max_retries=3
            )
            
            assert result is False
            # Should have 2 sleep calls (after 1st and 2nd failures, not after 3rd)
            assert len(sleep_times) == 2
            # Exponential backoff: 2^0=1, 2^1=2
            assert sleep_times[0] == 1
            assert sleep_times[1] == 2


def test_send_email_custom_max_retries(app):
    """Test that custom max_retries parameter is respected."""
    init_mail(app)
    
    call_count = 0
    def mock_send_always_fail(msg):
        nonlocal call_count
        call_count += 1
        raise Exception("SMTP error")
    
    with patch('src.email_service.mail.send', side_effect=mock_send_always_fail):
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = send_email(
                to="recipient@example.com",
                subject="Test Subject",
                body="Test body content",
                max_retries=5
            )
            
            assert result is False
            assert call_count == 5


def test_send_email_logs_retry_attempts(app, caplog):
    """Test that retry attempts are properly logged."""
    import logging
    init_mail(app)
    
    call_count = 0
    def mock_send_with_retry(msg):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary SMTP error")
        # Third call succeeds
    
    with caplog.at_level(logging.ERROR):
        with patch('src.email_service.mail.send', side_effect=mock_send_with_retry):
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = send_email(
                    to="recipient@example.com",
                    subject="Test Subject",
                    body="Test body content"
                )
                
                assert result is True
                # Should have logged 2 failures before success
                error_logs = [record for record in caplog.records if record.levelname == 'ERROR']
                assert len(error_logs) == 2
                assert "attempt 1/3" in error_logs[0].message
                assert "attempt 2/3" in error_logs[1].message


def test_send_email_logs_final_failure(app, caplog):
    """Test that final failure after all retries is properly logged."""
    import logging
    init_mail(app)
    
    def mock_send_always_fail(msg):
        raise Exception("Persistent SMTP error")
    
    with caplog.at_level(logging.ERROR):
        with patch('src.email_service.mail.send', side_effect=mock_send_always_fail):
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = send_email(
                    to="recipient@example.com",
                    subject="Test Subject",
                    body="Test body content",
                    max_retries=3
                )
                
                assert result is False
                # Should have logged 3 attempt failures + 1 final failure message
                error_logs = [record for record in caplog.records if record.levelname == 'ERROR']
                assert len(error_logs) == 4
                # Check final failure message
                assert "Failed to send email to recipient@example.com after 3 attempts" in error_logs[-1].message
                assert "Last error" in error_logs[-1].message


def test_send_email_logs_exception_type(app, caplog):
    """Test that exception type is logged for debugging."""
    import logging
    init_mail(app)
    
    def mock_send_with_specific_error(msg):
        raise ConnectionError("Connection refused")
    
    with caplog.at_level(logging.ERROR):
        with patch('src.email_service.mail.send', side_effect=mock_send_with_specific_error):
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = send_email(
                    to="recipient@example.com",
                    subject="Test Subject",
                    body="Test body content"
                )
                
                assert result is False
                # Check that exception type is logged
                error_logs = [record for record in caplog.records if record.levelname == 'ERROR']
                assert any("ConnectionError" in log.message for log in error_logs)
                assert any("Connection refused" in log.message for log in error_logs)
