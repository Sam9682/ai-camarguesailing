"""
Flask application setup for Camargue Sailing website.

This module initializes the Flask application with configuration,
session management, static files, and templates.

Requirements: 9.1, 9.3, 9.4, 9.5
"""

from flask import Flask
from src.config import Config
from src.database import db_session, close_db


def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    
    This factory function initializes the Flask app with:
    - Configuration from environment variables
    - Session management with secure cookies
    - Static files and templates directories
    - Database session cleanup
    
    Args:
        config_class: Configuration class to use (default: Config)
    
    Returns:
        Configured Flask application instance
    
    Requirements: 9.1, 9.3, 9.4, 9.5
    """
    # Initialize Flask app
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Configure session management
    # Flask uses SECRET_KEY for signing session cookies
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session expires after 1 hour
    
    # Register teardown function to close database session after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Close database session at the end of each request.
        
        This ensures database connections are properly cleaned up
        and prevents connection leaks.
        
        Args:
            exception: Any exception that occurred during the request
        """
        close_db()
    
    # Register blueprints (routes) here when they are created
    # Example:
    # from src.routes import public_bp, auth_bp, booking_bp, forum_bp
    # app.register_blueprint(public_bp)
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(booking_bp)
    # app.register_blueprint(forum_bp)
    
    # Temporary test route to verify base.html template
    @app.route('/test-base')
    def test_base():
        """Test route to verify base.html template rendering."""
        from flask import render_template
        return render_template('test_base.html')
    
    # Public routes
    @app.route('/')
    def home():
        """
        Home page route displaying sailing business overview.
        
        This route renders the home page with information about
        Camargue Sailing, including features, about section, and
        call-to-action for registration or booking.
        
        Requirements: 1.1
        """
        from flask import render_template
        return render_template('home.html')
    
    @app.route('/voyages')
    def voyages():
        """
        Voyages page route displaying one-week sailing voyage information.
        
        This route renders the voyages page with detailed information about
        one-week sailing trips in the South of France, including AMEL boat
        images, voyage details, typical itinerary, and what's included.
        
        Requirements: 1.2, 1.5
        """
        from flask import render_template
        return render_template('voyages.html')
    
    @app.route('/camargue')
    def camargue():
        """
        Camargue info page route displaying area information.
        
        This route renders the Camargue page with information about
        the Camargue area and Saintes-Maries-de-la-Mer, including
        regional features, attractions, and sailing context.
        
        Requirements: 1.3
        """
        from flask import render_template
        return render_template('camargue.html')
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the development server
    # In production, use a WSGI server like Gunicorn instead
    app.run(host='0.0.0.0', port=5000, debug=True)
