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
