"""
Unit tests for Flask application setup.

This module tests the Flask application initialization,
configuration, and session management.

Requirements: 9.1, 9.3, 9.4, 9.5
"""

import pytest
from src.app import create_app
from src.config import Config


def test_app_creation():
    """Test that the Flask app can be created successfully."""
    app = create_app()
    assert app is not None
    assert app.name == 'src.app'


def test_app_configuration():
    """Test that the Flask app loads configuration correctly."""
    app = create_app()
    
    # Verify SECRET_KEY is loaded
    assert app.config['SECRET_KEY'] is not None
    assert app.config['SECRET_KEY'] == Config.SECRET_KEY
    
    # Verify session configuration
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    assert app.config['PERMANENT_SESSION_LIFETIME'] == 3600


def test_static_folder_configuration():
    """Test that static files are configured correctly."""
    app = create_app()
    
    # Verify static folder is set
    assert app.static_folder is not None
    assert 'static' in app.static_folder


def test_template_folder_configuration():
    """Test that templates are configured correctly."""
    app = create_app()
    
    # Verify template folder is set
    assert app.template_folder is not None
    assert 'templates' in app.template_folder


def test_app_context():
    """Test that the app context works correctly."""
    app = create_app()
    
    with app.app_context():
        # Verify we can access app config within context
        assert app.config['SECRET_KEY'] is not None


def test_test_client():
    """Test that the test client can be created."""
    app = create_app()
    client = app.test_client()
    
    assert client is not None


def test_base_template_rendering():
    """Test that the base.html template renders correctly."""
    app = create_app()
    client = app.test_client()
    
    # Test the test_base route
    response = client.get('/test-base')
    
    assert response.status_code == 200
    assert b'Camargue Sailing' in response.data
    assert b'Base Template Test' in response.data


def test_base_template_navigation():
    """Test that the base template includes navigation menu."""
    app = create_app()
    client = app.test_client()
    
    response = client.get('/test-base')
    
    # Check for navigation links
    assert b'Home' in response.data
    assert b'Voyages' in response.data
    assert b'Camargue' in response.data
    assert b'Voyage Options' in response.data


def test_base_template_auth_display_guest():
    """Test that the base template shows auth options for guests."""
    app = create_app()
    client = app.test_client()
    
    response = client.get('/test-base')
    
    # Guest should see Sign In and Sign Up buttons
    assert b'Sign In' in response.data
    assert b'Sign Up' in response.data
    assert b'Sign Out' not in response.data


def test_base_template_css_reference():
    """Test that the base template includes CSS reference."""
    app = create_app()
    client = app.test_client()
    
    response = client.get('/test-base')
    
    # Check for CSS link
    assert b'style.css' in response.data


def test_base_template_image_reference():
    """Test that the base template includes AMEL boat image."""
    app = create_app()
    client = app.test_client()
    
    response = client.get('/test-base')
    
    # Check for AMEL image reference
    assert b'AMEL' in response.data
    assert b'.jpeg' in response.data



def test_base_template_auth_display_authenticated():
    """Test that the base template shows user info for authenticated users."""
    app = create_app()
    client = app.test_client()
    
    # Simulate an authenticated session
    with client.session_transaction() as session:
        session['user_id'] = 1
        session['user_email'] = 'test@example.com'
        session['is_verified'] = True
    
    response = client.get('/test-base')
    
    # Authenticated user should see welcome message and sign out
    assert b'Welcome, test@example.com' in response.data
    assert b'Sign Out' in response.data
    assert b'Sign In' not in response.data
    assert b'Sign Up' not in response.data
    # Should see protected pages in menu
    assert b'Calendar' in response.data
    assert b'Forum' in response.data


def test_base_template_unverified_badge():
    """Test that the base template shows unverified badge for unverified users."""
    app = create_app()
    client = app.test_client()
    
    # Simulate an unverified user session
    with client.session_transaction() as session:
        session['user_id'] = 1
        session['user_email'] = 'unverified@example.com'
        session['is_verified'] = False
    
    response = client.get('/test-base')
    
    # Should show unverified badge
    assert b'Unverified' in response.data
    assert b'unverified@example.com' in response.data
