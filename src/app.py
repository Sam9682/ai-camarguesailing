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
    
    @app.route('/voyage-options')
    def voyage_options():
        """
        Voyage options page route displaying different voyage options.
        
        This route renders the voyage options page with information about
        different types of sailing voyages available, including discovery
        voyages, learning voyages, and custom options. Includes AMEL boat
        images and detailed descriptions from the business plan.
        
        Requirements: 1.4, 1.5
        """
        from flask import render_template
        return render_template('voyage_options.html')
    
    # Authentication routes
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """
        Sign-up route for user registration.
        
        GET: Display registration form with email and password fields
        POST: Handle registration submission, create user account, send verification email
        
        This route validates registration data, checks for duplicate emails,
        creates unverified user accounts, and sends verification emails.
        
        Requirements: 2.1, 2.2, 2.3, 2.4
        """
        from flask import render_template, request, redirect, url_for, flash, session
        from src.auth import register_user, RegistrationError
        from src.email_service import send_verification_email
        
        # If user is already logged in, redirect to home
        if session.get('user_id'):
            flash('You are already logged in.', 'info')
            return redirect(url_for('home'))
        
        if request.method == 'GET':
            # Display registration form
            return render_template('signup.html')
        
        # Handle POST request - registration submission
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = {}
        
        # Validate that passwords match
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        # If there are validation errors, re-render form with errors
        if errors:
            return render_template('signup.html', errors=errors), 400
        
        try:
            # Attempt to register the user
            user = register_user(email, password)
            
            # Send verification email
            try:
                send_verification_email(user)
                flash('Registration successful! Please check your email to verify your account.', 'success')
            except Exception as e:
                # Log the error but don't fail registration
                app.logger.error(f'Failed to send verification email to {email}: {str(e)}')
                flash('Registration successful! However, we could not send the verification email. Please contact support.', 'warning')
            
            # Redirect to sign-in page
            return redirect(url_for('signin'))
            
        except RegistrationError as e:
            # Handle registration errors (duplicate email, validation failures)
            error_message = str(e)
            
            # Determine which field the error applies to
            if 'email' in error_message.lower() or 'already registered' in error_message.lower():
                errors['email'] = error_message
            elif 'password' in error_message.lower():
                errors['password'] = error_message
            else:
                # General error
                flash(error_message, 'error')
            
            return render_template('signup.html', errors=errors), 400
        
        except Exception as e:
            # Handle unexpected errors
            app.logger.error(f'Unexpected error during registration: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'error')
            return render_template('signup.html'), 500
    
    @app.route('/verify/<token>')
    def verify_email(token):
        """
        Email verification route.
        
        This route handles email verification by validating the token and marking
        the user's account as verified. On success, redirects to login page with
        a success message. On failure, displays an error message.
        
        Args:
            token: The verification token from the email link
        
        Requirements: 3.3, 3.4
        """
        from flask import redirect, url_for, flash
        from src.auth import verify_token
        
        # Attempt to verify the token
        user_id = verify_token(token)
        
        if user_id:
            # Verification successful
            flash('Email verified successfully! You can now sign in.', 'success')
            return redirect(url_for('signin'))
        else:
            # Verification failed (invalid or expired token)
            flash('Invalid or expired verification link. Please request a new verification email.', 'error')
            return redirect(url_for('home'))
    
    @app.route('/signin', methods=['GET', 'POST'])
    def signin():
        """
        Sign-in route for user authentication.
        
        GET: Display login form with email and password fields
        POST: Handle authentication submission, create session for verified users
        
        This route validates credentials, checks email verification status,
        and creates a session for authenticated users.
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        from flask import render_template, request, redirect, url_for, flash, session
        from src.auth import authenticate_user, AuthenticationError
        
        # If user is already logged in, redirect to home
        if session.get('user_id'):
            flash('You are already logged in.', 'info')
            return redirect(url_for('home'))
        
        if request.method == 'GET':
            # Display login form
            return render_template('signin.html')
        
        # Handle POST request - authentication submission
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        errors = {}
        
        try:
            # Attempt to authenticate the user
            user = authenticate_user(email, password)
            
            # Authentication successful - create session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session.permanent = True  # Use PERMANENT_SESSION_LIFETIME from config
            
            flash('Welcome back! You have successfully signed in.', 'success')
            
            # Redirect to home page or to the page they were trying to access
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
            
        except AuthenticationError as e:
            # Handle authentication errors
            error_message = str(e)
            
            # Determine which field the error applies to
            if 'email' in error_message.lower() and 'password' in error_message.lower():
                # Generic "incorrect email or password" error
                errors['email'] = error_message
            elif 'verification' in error_message.lower():
                # Email verification required error
                flash(error_message, 'error')
            else:
                # Other authentication errors
                flash(error_message, 'error')
            
            return render_template('signin.html', errors=errors), 401
        
        except Exception as e:
            # Handle unexpected errors
            app.logger.error(f'Unexpected error during sign-in: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'error')
            return render_template('signin.html'), 500
    @app.route('/signout')
    def signout():
        """
        Sign-out route to terminate user session.

        This route clears the user's session data, effectively logging them out,
        and redirects to the home page with a confirmation message.

        Requirements: 4.5
        """
        from flask import redirect, url_for, flash, session

        # Check if user was logged in
        was_logged_in = 'user_id' in session

        # Clear all session data
        session.clear()

        # Show confirmation message only if user was actually logged in
        if was_logged_in:
            flash('You have been successfully signed out.', 'success')

        # Redirect to home page
        return redirect(url_for('home'))
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the development server
    # In production, use a WSGI server like Gunicorn instead
    app.run(host='0.0.0.0', port=5000, debug=True)
