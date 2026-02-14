"""
Internationalization (i18n) module for Camargue Sailing website.

This module provides bilingual support (English/French) using Flask-Babel.
"""

from flask_babel import Babel
from flask import request, session

babel = Babel()


def get_locale():
    """
    Determine the user's preferred language.
    
    Priority:
    1. Language stored in session (user's explicit choice)
    2. Browser's Accept-Language header
    3. Default to English
    
    Returns:
        str: Language code ('en' or 'fr')
    """
    # Check if user has explicitly selected a language
    if 'language' in session:
        return session['language']
    
    # Try to match browser's preferred language
    return request.accept_languages.best_match(['en', 'fr']) or 'en'


def init_babel(app):
    """
    Initialize Flask-Babel with the Flask application.
    
    Args:
        app: Flask application instance
    """
    babel.init_app(app, locale_selector=get_locale)
