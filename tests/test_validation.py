"""
Unit tests for form validation across all routes.

This module tests validation for email format, password strength,
date ranges, and form field requirements.

Requirements: 2.4, 7.3
"""

import pytest
from datetime import date, timedelta
from src.app import create_app
from src.database import Base, engine, db_session
from src.models import User, ForumPost


@pytest.fixture
def setup_database():
    """Set up a clean database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


class TestSignupValidation:
    """Test validation for signup route."""
    
    def test_signup_invalid_email_format(self, setup_database):
        """Test that signup rejects invalid email formats."""
        app = create_app()
        client = app.test_client()
        
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@nodomain.com',
            'spaces in@email.com',
            'double@@domain.com'
        ]
        
        for email in invalid_emails:
            response = client.post('/signup', data={
                'email': email,
                'password': 'password123',
                'confirm_password': 'password123'
            })
            
            assert response.status_code == 400
            assert b'Invalid email format' in response.data or b'Email' in response.data
    
    def test_signup_empty_email(self, setup_database):
        """Test that signup rejects empty email."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signup', data={
            'email': '',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_signup_short_password(self, setup_database):
        """Test that signup rejects passwords shorter than 8 characters."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signup', data={
            'email': 'test@example.com',
            'password': 'short',
            'confirm_password': 'short'
        })
        
        assert response.status_code == 400
        assert b'at least 8 characters' in response.data
    
    def test_signup_empty_password(self, setup_database):
        """Test that signup rejects empty password."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signup', data={
            'email': 'test@example.com',
            'password': '',
            'confirm_password': ''
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_signup_password_mismatch(self, setup_database):
        """Test that signup rejects mismatched passwords."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signup', data={
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different123'
        })
        
        assert response.status_code == 400
        assert b'do not match' in response.data
    
    def test_signup_multiple_validation_errors(self, setup_database):
        """Test that signup shows multiple validation errors."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signup', data={
            'email': 'invalid-email',
            'password': 'short',
            'confirm_password': 'different'
        })
        
        assert response.status_code == 400
        # Should show errors for both email and password
        assert b'email' in response.data.lower() or b'Email' in response.data
        assert b'password' in response.data.lower() or b'Password' in response.data


class TestSigninValidation:
    """Test validation for signin route."""
    
    def test_signin_invalid_email_format(self, setup_database):
        """Test that signin rejects invalid email formats."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signin', data={
            'email': 'notanemail',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        assert b'Invalid email format' in response.data or b'email' in response.data.lower()
    
    def test_signin_empty_email(self, setup_database):
        """Test that signin rejects empty email."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signin', data={
            'email': '',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_signin_empty_password(self, setup_database):
        """Test that signin rejects empty password."""
        app = create_app()
        client = app.test_client()
        
        response = client.post('/signin', data={
            'email': 'test@example.com',
            'password': ''
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()


class TestBookingValidation:
    """Test validation for booking route."""
    
    def test_book_empty_start_date(self, setup_database):
        """Test that booking rejects empty start date."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        response = client.post('/book', data={
            'start_date': '',
            'end_date': '2025-12-31'
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_book_empty_end_date(self, setup_database):
        """Test that booking rejects empty end date."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        response = client.post('/book', data={
            'start_date': '2025-12-01',
            'end_date': ''
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_book_invalid_date_format(self, setup_database):
        """Test that booking rejects invalid date formats."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        invalid_dates = [
            ('12/01/2025', '12/31/2025'),  # Wrong format
            ('2025-13-01', '2025-12-31'),  # Invalid month
            ('2025-12-32', '2025-12-31'),  # Invalid day
            ('not-a-date', '2025-12-31'),  # Not a date
        ]
        
        for start, end in invalid_dates:
            response = client.post('/book', data={
                'start_date': start,
                'end_date': end
            })
            
            assert response.status_code == 400
            assert b'Invalid date format' in response.data or b'date' in response.data.lower()
    
    def test_book_past_start_date(self, setup_database):
        """Test that booking rejects past start dates."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        # Try to book a date in the past
        past_date = (date.today() - timedelta(days=1)).isoformat()
        future_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.post('/book', data={
            'start_date': past_date,
            'end_date': future_date
        })
        
        assert response.status_code == 400
        assert b'past' in response.data.lower()
    
    def test_book_end_before_start(self, setup_database):
        """Test that booking rejects end date before start date."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        # Try to book with end date before start date
        start_date = (date.today() + timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        
        response = client.post('/book', data={
            'start_date': start_date,
            'end_date': end_date
        })
        
        assert response.status_code == 400
        assert b'after' in response.data.lower() or b'before' in response.data.lower()
    
    def test_book_same_start_and_end_date(self, setup_database):
        """Test that booking rejects same start and end date."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        # Try to book with same start and end date
        same_date = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.post('/book', data={
            'start_date': same_date,
            'end_date': same_date
        })
        
        assert response.status_code == 400
        assert b'after' in response.data.lower()


class TestForumValidation:
    """Test validation for forum routes."""
    
    def test_new_post_empty_title(self, setup_database):
        """Test that new post rejects empty title."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        response = client.post('/forum/new', data={
            'title': '',
            'content': 'This is the content'
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_new_post_empty_content(self, setup_database):
        """Test that new post rejects empty content."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        response = client.post('/forum/new', data={
            'title': 'Test Title',
            'content': ''
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_new_post_title_too_long(self, setup_database):
        """Test that new post rejects titles longer than 255 characters."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        # Create a title longer than 255 characters
        long_title = 'A' * 256
        
        response = client.post('/forum/new', data={
            'title': long_title,
            'content': 'This is the content'
        })
        
        assert response.status_code == 400
        assert b'too long' in response.data.lower() or b'maximum' in response.data.lower()
    
    def test_reply_empty_content(self, setup_database):
        """Test that reply rejects empty content."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        # Create a forum post
        post = ForumPost(user_id=user_id, title='Test Post', content='Test content')
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': ''
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower()
    
    def test_reply_whitespace_only_content(self, setup_database):
        """Test that reply rejects whitespace-only content."""
        app = create_app()
        client = app.test_client()
        
        # Create and login a verified user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        user_email = user.email
        
        # Create a forum post
        post = ForumPost(user_id=user_id, title='Test Post', content='Test content')
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = user_email
        
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': '   '
        })
        
        assert response.status_code == 400
        assert b'required' in response.data.lower() or b'empty' in response.data.lower()
