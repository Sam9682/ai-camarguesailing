"""
Flask application setup for Camargue Sailing website.

This module initializes the Flask application with configuration,
session management, static files, and templates.

Requirements: 9.1, 9.3, 9.4, 9.5
"""

from flask import Flask, session, redirect, url_for, request
from src.config import Config
from src.database import db_session, close_db
from src.i18n import init_babel


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
    
    # Initialize Flask-Babel for internationalization
    init_babel(app)
    
    # Configure Babel
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr']
    
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
    
    # Language switching route
    @app.route('/set-language/<lang>')
    def set_language(lang):
        """
        Set the user's preferred language.
        
        This route stores the selected language in the session and redirects
        back to the referring page or home page.
        
        Args:
            lang: Language code ('en' or 'fr')
        """
        if lang in ['en', 'fr']:
            session['language'] = lang
        
        # Redirect back to the referring page or home
        return redirect(request.referrer or url_for('home'))
    
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
        
        # Validate email format before checking password match
        from src.auth import validate_email, validate_password
        email_valid, email_error = validate_email(email)
        if not email_valid:
            errors['email'] = email_error
        
        # Validate password strength
        password_valid, password_error = validate_password(password)
        if not password_valid:
            errors['password'] = password_error
        
        # Validate that passwords match
        if password and confirm_password and password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        # If there are validation errors, re-render form with errors
        if errors:
            return render_template('signup.html', errors=errors, email=email), 400
        
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
        
        # Validate email format
        from src.auth import validate_email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            errors['email'] = email_error
            return render_template('signin.html', errors=errors, email=email), 400
        
        # Validate password is provided
        if not password:
            errors['password'] = 'Password is required'
            return render_template('signin.html', errors=errors, email=email), 400
        
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
    
    # Booking routes
    from src.auth import login_required, verified_required
    
    @app.route('/calendar')
    @login_required
    @verified_required
    def calendar():
        """
        Calendar route displaying yearly planning with booked/available periods.
        
        This route renders the calendar page showing all bookings for the current year.
        The calendar displays booked periods and available periods, allowing users to
        see voyage availability at a glance.
        
        This route is protected and requires both authentication and email verification.
        
        Requirements: 6.1, 6.2, 6.3
        """
        from flask import render_template
        from datetime import datetime
        from src.booking import get_calendar_data
        
        # Get current year
        current_year = datetime.now().year
        
        # Fetch calendar data for the current year
        calendar_data = get_calendar_data(current_year)
        
        # Render calendar template with data
        return render_template('calendar.html', 
                             calendar_data=calendar_data, 
                             year=current_year)
    
    @app.route('/book', methods=['GET', 'POST'])
    @login_required
    @verified_required
    def book():
        """
        Booking route for creating new voyage reservations.
        
        GET: Display booking form with date selection fields
        POST: Handle booking creation with validation and error handling
        
        This route allows verified users to create bookings by selecting start and end dates.
        It validates date ranges, checks for overlapping bookings, and sends confirmation emails.
        
        This route is protected and requires both authentication and email verification.
        
        Requirements: 7.1, 7.2
        """
        from flask import render_template, request, redirect, url_for, flash, session
        from datetime import datetime
        from src.booking import create_booking
        from src.email_service import send_booking_confirmation
        from src.database import db_session
        
        if request.method == 'GET':
            # Display booking form
            return render_template('book.html')
        
        # Handle POST request - booking submission
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        
        errors = {}
        
        # Validate that dates are provided
        if not start_date_str:
            errors['start_date'] = 'Start date is required'
        if not end_date_str:
            errors['end_date'] = 'End date is required'
        
        # If there are validation errors, re-render form with errors
        if errors:
            return render_template('book.html', errors=errors), 400
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors['start_date'] = 'Invalid date format. Please use YYYY-MM-DD format.'
        
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors['end_date'] = 'Invalid date format. Please use YYYY-MM-DD format.'
        
        # If date parsing failed, re-render form with errors
        if errors:
            return render_template('book.html', errors=errors, 
                                 start_date=start_date_str, 
                                 end_date=end_date_str), 400
        
        # Get user_id from session
        user_id = session.get('user_id')
        
        try:
            # Attempt to create the booking
            booking = create_booking(user_id, start_date, end_date)
            
            # Get the user object for email sending
            from src.models import User
            user = db_session.query(User).filter_by(id=user_id).first()
            
            # Send booking confirmation email
            try:
                send_booking_confirmation(booking, user)
            except Exception as e:
                # Log the error but don't fail the booking
                app.logger.error(f'Failed to send booking confirmation email: {str(e)}')
                flash('Booking created successfully! However, we could not send the confirmation email. Please contact support.', 'warning')
            else:
                flash('Booking created successfully! A confirmation email has been sent.', 'success')
            
            # Redirect to calendar on success
            return redirect(url_for('calendar'))
            
        except ValueError as e:
            # Handle booking errors (overlapping bookings, invalid dates)
            error_message = str(e)
            
            # Determine which field the error applies to
            if 'overlap' in error_message.lower() or 'not available' in error_message.lower():
                errors['general'] = error_message
                flash(error_message, 'error')
            elif 'end date' in error_message.lower():
                errors['end_date'] = error_message
            elif 'start date' in error_message.lower():
                errors['start_date'] = error_message
            else:
                errors['general'] = error_message
                flash(error_message, 'error')
            
            return render_template('book.html', errors=errors, 
                                 start_date=start_date_str, 
                                 end_date=end_date_str), 400
        
        except Exception as e:
            # Handle unexpected errors
            app.logger.error(f'Unexpected error during booking creation: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'error')
            return render_template('book.html', 
                                 start_date=start_date_str, 
                                 end_date=end_date_str), 500
    
    # Forum routes
    @app.route('/forum')
    @login_required
    @verified_required
    def forum():
        """
        Forum route displaying all discussion posts.
        
        This route renders the forum page showing all forum posts with their authors,
        timestamps, and replies. The page is protected and requires both authentication
        and email verification.
        
        Requirements: 8.1, 8.3, 8.6
        """
        from flask import render_template
        from src.forum import get_all_posts
        
        # Fetch all forum posts with replies
        posts = get_all_posts()
        
        # Render forum template with posts
        return render_template('forum.html', calendar_data=posts)
    
    @app.route('/forum/new', methods=['GET', 'POST'])
    @login_required
    @verified_required
    def new_post():
        """
        New post route for creating forum posts.
        
        GET: Display post creation form with title and content fields
        POST: Handle post creation with validation and error handling
        
        This route allows verified users to create new forum posts by providing
        a title and content. It validates the input, creates the post, and redirects
        to the forum page on success.
        
        This route is protected and requires both authentication and email verification.
        
        Requirements: 8.2
        """
        from flask import render_template, request, redirect, url_for, flash, session
        from src.forum import create_post
        
        if request.method == 'GET':
            # Display post creation form
            return render_template('new_post.html')
        
        # Handle POST request - post creation submission
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        errors = {}
        
        # Validate that fields are provided
        if not title:
            errors['title'] = 'Title is required'
        elif len(title) > 255:
            errors['title'] = 'Title is too long (maximum 255 characters)'
        
        if not content:
            errors['content'] = 'Content is required'
        
        # If there are validation errors, re-render form with errors
        if errors:
            return render_template('new_post.html', errors=errors, 
                                 title=title, content=content), 400
        
        # Get user_id from session
        user_id = session.get('user_id')
        
        try:
            # Attempt to create the post
            post = create_post(user_id, title, content)
            
            flash('Post created successfully!', 'success')
            
            # Redirect to forum on success
            return redirect(url_for('forum'))
            
        except ValueError as e:
            # Handle post creation errors (validation failures)
            error_message = str(e)
            
            # Determine which field the error applies to
            if 'title' in error_message.lower():
                errors['title'] = error_message
            elif 'content' in error_message.lower():
                errors['content'] = error_message
            else:
                errors['general'] = error_message
                flash(error_message, 'error')
            
            return render_template('new_post.html', errors=errors, 
                                 title=title, content=content), 400
        
        except Exception as e:
            # Handle unexpected errors
            app.logger.error(f'Unexpected error during post creation: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'error')
            return render_template('new_post.html', 
                                 title=title, content=content), 500
    
    @app.route('/forum/<int:post_id>/reply', methods=['GET', 'POST'])
    @login_required
    @verified_required
    def reply_to_post(post_id):
        """
        Reply route for adding replies to forum posts.
        
        GET: Display reply form for a specific post
        POST: Handle reply creation with validation and error handling
        
        This route allows verified users to reply to existing forum posts.
        It validates the content, creates the reply, and redirects to the
        forum page on success.
        
        This route is protected and requires both authentication and email verification.
        
        Args:
            post_id: ID of the post being replied to
        
        Requirements: 8.4
        """
        from flask import render_template, request, redirect, url_for, flash, session
        from src.forum import create_reply, get_all_posts
        from src.database import db_session
        from src.models import ForumPost
        
        # Get the post to verify it exists
        post = db_session.query(ForumPost).filter_by(id=post_id).first()
        
        if not post:
            flash('Post not found.', 'error')
            return redirect(url_for('forum'))
        
        if request.method == 'GET':
            # Display reply form
            return render_template('reply.html', post=post)
        
        # Handle POST request - reply submission
        content = request.form.get('content', '').strip()
        
        errors = {}
        
        # Validate that content is provided
        if not content:
            errors['content'] = 'Reply content is required'
        elif len(content) == 0:
            errors['content'] = 'Reply content cannot be empty'
        
        # If there are validation errors, re-render form with errors
        if errors:
            return render_template('reply.html', post=post, errors=errors, 
                                 content=content), 400
        
        # Get user_id from session
        user_id = session.get('user_id')
        
        try:
            # Attempt to create the reply
            reply = create_reply(post_id, user_id, content)
            
            flash('Reply posted successfully!', 'success')
            
            # Redirect to forum on success
            return redirect(url_for('forum'))
            
        except ValueError as e:
            # Handle reply creation errors (validation failures)
            error_message = str(e)
            
            # Determine which field the error applies to
            if 'content' in error_message.lower():
                errors['content'] = error_message
            elif 'post' in error_message.lower() and 'not exist' in error_message.lower():
                # Post was deleted between GET and POST
                flash(error_message, 'error')
                return redirect(url_for('forum'))
            else:
                errors['general'] = error_message
                flash(error_message, 'error')
            
            return render_template('reply.html', post=post, errors=errors, 
                                 content=content), 400
        
        except Exception as e:
            # Handle unexpected errors
            app.logger.error(f'Unexpected error during reply creation: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'error')
            return render_template('reply.html', post=post, content=content), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Handle 404 Not Found errors.
        
        This handler is triggered when a requested page or resource
        does not exist on the server.
        
        Args:
            error: The error object
        
        Returns:
            Rendered error page with 404 status code
        """
        from flask import render_template
        return render_template('error.html',
                             error_code=404,
                             error_title='Page Not Found',
                             error_message='The page you are looking for does not exist. It may have been moved or deleted.'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 Internal Server Error.
        
        This handler is triggered when an unexpected error occurs
        on the server during request processing.
        
        Args:
            error: The error object
        
        Returns:
            Rendered error page with 500 status code
        """
        from flask import render_template
        from src.database import db_session
        
        # Rollback any pending database transactions
        db_session.rollback()
        
        # Log the error
        app.logger.error(f'Internal server error: {str(error)}')
        
        return render_template('error.html',
                             error_code=500,
                             error_title='Internal Server Error',
                             error_message='An unexpected error occurred on the server. Please try again later.'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """
        Handle 403 Forbidden errors.
        
        This handler is triggered when a user attempts to access
        a resource they do not have permission to access.
        
        Args:
            error: The error object
        
        Returns:
            Rendered error page with 403 status code
        """
        from flask import render_template
        return render_template('error.html',
                             error_code=403,
                             error_title='Forbidden',
                             error_message='You do not have permission to access this resource.'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """
        Handle 401 Unauthorized errors.
        
        This handler is triggered when authentication is required
        but not provided or is invalid.
        
        Args:
            error: The error object
        
        Returns:
            Rendered error page with 401 status code
        """
        from flask import render_template
        return render_template('error.html',
                             error_code=401,
                             error_title='Unauthorized',
                             error_message='Authentication is required to access this resource. Please sign in to continue.'), 401
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the development server
    # In production, use a WSGI server like Gunicorn instead
    app.run(host='0.0.0.0', port=5000, debug=True)
