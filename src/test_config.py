"""
Unit tests for configuration module.

Tests environment variable loading and validation.
"""

import pytest
import os
from unittest.mock import patch


def test_config_loads_required_variables():
    """Test that Config class loads all required environment variables."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test-password',
        'MAIL_DEFAULT_SENDER': 'test@example.com'
    }):
        # Reimport to pick up new environment variables
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config
        
        assert Config.SECRET_KEY == 'test-secret-key'
        assert Config.DATABASE_URL == 'postgresql://test:test@localhost/test'
        assert Config.MAIL_USERNAME == 'test@example.com'
        assert Config.MAIL_PASSWORD == 'test-password'


def test_config_raises_error_without_secret_key():
    """Test that Config raises ValueError when SECRET_KEY is missing."""
    with patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test-password'
    }, clear=True):
        with pytest.raises(ValueError, match="SECRET_KEY environment variable is required"):
            import importlib
            import src.config
            importlib.reload(src.config)


def test_config_raises_error_without_database_url():
    """Test that Config raises ValueError when DATABASE_URL is missing."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test-password'
    }, clear=True):
        with pytest.raises(ValueError, match="DATABASE_URL environment variable is required"):
            import importlib
            import src.config
            importlib.reload(src.config)


def test_config_raises_error_without_mail_credentials():
    """Test that Config raises ValueError when email credentials are missing."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'postgresql://test:test@localhost/test'
    }, clear=True):
        with pytest.raises(ValueError, match="MAIL_USERNAME and MAIL_PASSWORD environment variables are required"):
            import importlib
            import src.config
            importlib.reload(src.config)


def test_config_uses_default_values():
    """Test that Config uses default values for optional settings."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test-password'
    }):
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config
        
        assert Config.MAIL_SERVER == 'smtp.gmail.com'
        assert Config.MAIL_PORT == 587
        assert Config.MAIL_USE_TLS is True
        assert Config.BASE_URL == 'http://localhost:5000'
        assert Config.VERIFICATION_TOKEN_EXPIRY_HOURS == 24


def test_config_parses_mail_port_as_integer():
    """Test that MAIL_PORT is correctly parsed as an integer."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test-password',
        'MAIL_PORT': '465'
    }):
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config
        
        assert Config.MAIL_PORT == 465
        assert isinstance(Config.MAIL_PORT, int)


def test_config_parses_mail_use_tls_as_boolean():
    """Test that MAIL_USE_TLS is correctly parsed as a boolean."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test-password',
        'MAIL_USE_TLS': 'False'
    }):
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config
        
        assert Config.MAIL_USE_TLS is False
