"""
Internationalization (i18n) module for Camargue Sailing website.

This module provides bilingual support (English/French) using Flask-Babel.
"""

from flask_babel import Babel
from flask import request, session


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
        locale = session['language']
        print(f"[i18n] Using session language: {locale}")
        return locale
    
    # Try to match browser's preferred language
    locale = request.accept_languages.best_match(['en', 'fr']) or 'en'
    print(f"[i18n] Using browser language: {locale}")
    return locale


def init_babel(app):
    """
    Initialize Flask-Babel with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Initialize Babel with locale selector
    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)
    
    return babel
