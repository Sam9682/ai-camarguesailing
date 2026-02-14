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


def test_home_page_route():
    """
    Test that the home page route renders successfully.
    
    Requirements: 1.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/')
    
    # Verify successful response
    assert response.status_code == 200
    
    # Verify home page content is present
    assert b'Welcome to Camargue Sailing' in response.data
    assert b'Experience the Magic of the Mediterranean' in response.data


def test_home_page_business_overview():
    """
    Test that the home page displays sailing business overview.
    
    Requirements: 1.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/')
    
    # Verify business overview content
    assert b'About Our Sailing Business' in response.data
    assert b'Camargue Sailing offers authentic sailing experiences' in response.data
    assert b'Saintes-Maries-de-la-Mer' in response.data
    assert b'one-week sailing voyages' in response.data


def test_home_page_features():
    """
    Test that the home page displays key features.
    
    Requirements: 1.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/')
    
    # Verify features section
    assert b'Why Choose Camargue Sailing?' in response.data
    assert b'Premium AMEL Yacht' in response.data
    assert b'Mediterranean Beauty' in response.data
    assert b'Expert Skipper' in response.data
    assert b'One-Week Voyages' in response.data


def test_home_page_includes_amel_images():
    """
    Test that the home page includes AMEL boat images.
    
    Requirements: 1.1, 1.5
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/')
    
    # Verify AMEL images are referenced
    assert b'AMEL' in response.data
    assert b'.jpeg' in response.data
    assert b'images/AMEL' in response.data


def test_home_page_call_to_action():
    """
    Test that the home page includes call-to-action elements.
    
    Requirements: 1.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/')
    
    # Verify CTA section
    assert b'Ready to Set Sail?' in response.data
    assert b'Explore Voyages' in response.data or b'View Calendar' in response.data


def test_camargue_page_route():
    """
    Test that the Camargue info page route renders successfully.
    
    Requirements: 1.3
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/camargue')
    
    # Verify successful response
    assert response.status_code == 200
    
    # Verify Camargue page content is present
    assert b'The Camargue Region' in response.data
    assert b'Saintes-Maries-de-la-Mer' in response.data


def test_camargue_page_area_information():
    """
    Test that the Camargue page displays area information.
    
    Requirements: 1.3
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/camargue')
    
    # Verify Camargue area information
    assert b'Discover the Camargue' in response.data
    assert b'natural region in the South of France' in response.data
    assert b'Rh\xc3\xb4ne River' in response.data or b'Rhone River' in response.data
    assert b'Mediterranean Sea' in response.data


def test_camargue_page_natural_features():
    """
    Test that the Camargue page displays natural features.
    
    Requirements: 1.3
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/camargue')
    
    # Verify natural features are described
    assert b'Pink Flamingos' in response.data or b'flamingos' in response.data
    assert b'White Horses' in response.data or b'Camargue horses' in response.data
    assert b'Black Bulls' in response.data or b'bulls' in response.data


def test_camargue_page_saintes_maries_info():
    """
    Test that the Camargue page displays Saintes-Maries-de-la-Mer information.
    
    Requirements: 1.3
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/camargue')
    
    # Verify Saintes-Maries-de-la-Mer information
    assert b'Saintes-Maries-de-la-Mer' in response.data
    assert b'home port' in response.data or b'capital of the Camargue' in response.data
    assert b'village' in response.data
    assert b'marina' in response.data or b'Marina' in response.data


def test_camargue_page_sailing_context():
    """
    Test that the Camargue page provides sailing context.
    
    Requirements: 1.3
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/camargue')
    
    # Verify sailing context is provided
    assert b'Sailing from the Camargue' in response.data or b'sailing' in response.data
    assert b'Mediterranean' in response.data


def test_camargue_page_accessible_without_auth():
    """
    Test that the Camargue page is accessible without authentication.
    
    Requirements: 1.3, 1.6
    """
    app = create_app()
    client = app.test_client()
    
    # Access without authentication
    response = client.get('/camargue')
    
    # Should return 200, not redirect to login
    assert response.status_code == 200
    assert b'The Camargue Region' in response.data


def test_voyage_options_page_route():
    """
    Test that the voyage options page route renders successfully.
    
    Requirements: 1.4
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/voyage-options')
    
    # Verify successful response
    assert response.status_code == 200
    
    # Verify voyage options page content is present
    assert b'Voyage Options' in response.data
    assert b'Choose the Perfect Sailing Experience' in response.data


def test_voyage_options_displays_different_options():
    """
    Test that the voyage options page displays different voyage types.
    
    Requirements: 1.4
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/voyage-options')
    
    # Verify different voyage options are displayed
    assert b'Discovery Voyage' in response.data
    assert b'Learning Voyage' in response.data
    assert b'Relaxation Voyage' in response.data
    assert b'Custom Voyage' in response.data


def test_voyage_options_includes_amel_images():
    """
    Test that the voyage options page includes AMEL boat images.
    
    Requirements: 1.4, 1.5
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/voyage-options')
    
    # Verify AMEL images are referenced
    assert b'AMEL' in response.data
    assert b'.jpeg' in response.data
    assert b'images/AMEL' in response.data
    
    # Verify multiple images are included
    assert response.data.count(b'images/AMEL') >= 4


def test_voyage_options_displays_details():
    """
    Test that the voyage options page displays detailed information.
    
    Requirements: 1.4
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/voyage-options')
    
    # Verify detailed information is present
    assert b'Duration:' in response.data
    assert b'Experience Level:' in response.data
    assert b'Group Size:' in response.data
    assert b'Highlights:' in response.data


def test_voyage_options_includes_comparison():
    """
    Test that the voyage options page includes comparison information.
    
    Requirements: 1.4
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/voyage-options')
    
    # Verify comparison section is present
    assert b'Compare Voyage Options' in response.data
    assert b'Discovery' in response.data
    assert b'Learning' in response.data
    assert b'Relaxation' in response.data
    assert b'Custom' in response.data


def test_voyage_options_accessible_without_auth():
    """
    Test that the voyage options page is accessible without authentication.
    
    Requirements: 1.4, 1.6
    """
    app = create_app()
    client = app.test_client()
    
    # Access without authentication
    response = client.get('/voyage-options')
    
    # Should return 200, not redirect to login
    assert response.status_code == 200
    assert b'Voyage Options' in response.data



def test_signup_page_get():
    """
    Test that the signup page displays the registration form.
    
    Requirements: 2.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/signup')
    
    # Verify successful response
    assert response.status_code == 200
    
    # Verify signup form is present
    assert b'Create Your Account' in response.data
    assert b'Email Address' in response.data
    assert b'Password' in response.data
    assert b'Confirm Password' in response.data
    assert b'Sign Up' in response.data


def test_signup_page_accessible_without_auth():
    """
    Test that the signup page is accessible without authentication.
    
    Requirements: 2.1
    """
    app = create_app()
    client = app.test_client()
    
    # Access without authentication
    response = client.get('/signup')
    
    # Should return 200, not redirect
    assert response.status_code == 200
    assert b'Create Your Account' in response.data


def test_signup_redirects_if_logged_in():
    """
    Test that the signup page redirects if user is already logged in.
    
    Requirements: 2.1
    """
    app = create_app()
    client = app.test_client()
    
    # Simulate an authenticated session
    with client.session_transaction() as session:
        session['user_id'] = 1
        session['user_email'] = 'test@example.com'
    
    response = client.get('/signup')
    
    # Should redirect to home
    assert response.status_code == 302
    assert response.location == '/' or response.location.endswith('/')


def test_signup_includes_signin_link():
    """
    Test that the signup page includes a link to sign in.
    
    Requirements: 2.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/signup')
    
    # Verify sign in link is present
    assert b'Already have an account?' in response.data
    assert b'Sign In' in response.data
    assert b'/signin' in response.data



def test_signup_post_password_mismatch():
    """
    Test that signup rejects mismatched passwords.
    
    Requirements: 2.4
    """
    app = create_app()
    client = app.test_client()
    
    response = client.post('/signup', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'different123'
    })
    
    # Should return 400 with error
    assert response.status_code == 400
    assert b'Passwords do not match' in response.data


def test_signup_form_preserves_email_on_error():
    """
    Test that signup form preserves email on validation error.
    
    Requirements: 2.4
    """
    app = create_app()
    client = app.test_client()
    
    response = client.post('/signup', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'different123'
    })
    
    # Email should be preserved in the form
    assert b'test@example.com' in response.data



def test_verify_email_success():
    """
    Test that email verification succeeds with valid token.
    
    Requirements: 3.3
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from src.auth import generate_verification_token
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a test user
        user = User(email='test@example.com', is_verified=False)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Generate verification token
        token = generate_verification_token(user_id)
        
        # Verify the email
        response = client.get(f'/verify/{token}', follow_redirects=False)
        
        # Should redirect to signin
        assert response.status_code == 302
        assert '/signin' in response.location
        
        # Check that user is now verified (query fresh from database)
        verified_user = db_session.query(User).filter_by(id=user_id).first()
        assert verified_user.is_verified is True
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_verify_email_invalid_token():
    """
    Test that email verification fails with invalid token.
    
    Requirements: 3.4
    """
    from src.database import Base, engine, db_session
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Try to verify with invalid token
        response = client.get('/verify/invalid_token_12345', follow_redirects=False)
        
        # Should redirect to home
        assert response.status_code == 302
        assert '/' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_verify_email_expired_token():
    """
    Test that email verification fails with expired token.
    
    Requirements: 3.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, VerificationToken
    from datetime import datetime, timedelta
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a test user
        user = User(email='test@example.com', is_verified=False)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Create an expired token
        expired_token = VerificationToken(
            user_id=user_id,
            token='expired_token_12345',
            expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        )
        db_session.add(expired_token)
        db_session.commit()
        
        # Try to verify with expired token
        response = client.get('/verify/expired_token_12345', follow_redirects=False)
        
        # Should redirect to home
        assert response.status_code == 302
        assert '/' in response.location
        
        # User should still be unverified (query fresh from database)
        verified_user = db_session.query(User).filter_by(id=user_id).first()
        assert verified_user.is_verified is False
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_verify_email_success_message():
    """
    Test that successful verification shows success message.
    
    Requirements: 3.3
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from src.auth import generate_verification_token
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a test user
        user = User(email='test@example.com', is_verified=False)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Generate verification token
        token = generate_verification_token(user.id)
        
        # Verify the email (don't follow redirects to check flash message)
        with client.session_transaction() as sess:
            pass  # Initialize session
        
        response = client.get(f'/verify/{token}', follow_redirects=False)
        
        # Check that flash message was set
        with client.session_transaction() as sess:
            flashes = dict(sess.get('_flashes', []))
            assert any('verified' in str(msg).lower() for msg in flashes.values())
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_verify_email_error_message():
    """
    Test that failed verification shows error message.
    
    Requirements: 3.4
    """
    from src.database import Base, engine, db_session
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Try to verify with invalid token (don't follow redirects to check flash message)
        with client.session_transaction() as sess:
            pass  # Initialize session
        
        response = client.get('/verify/invalid_token_12345', follow_redirects=False)
        
        # Check that flash message was set
        with client.session_transaction() as sess:
            flashes = dict(sess.get('_flashes', []))
            assert any('invalid' in str(msg).lower() or 'expired' in str(msg).lower() for msg in flashes.values())
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_page_get():
    """
    Test that the signin page displays the login form.
    
    Requirements: 4.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/signin')
    
    # Verify successful response
    assert response.status_code == 200
    
    # Verify signin form is present
    assert b'Welcome Back' in response.data
    assert b'Email Address' in response.data
    assert b'Password' in response.data
    assert b'Sign In' in response.data


def test_signin_page_accessible_without_auth():
    """
    Test that the signin page is accessible without authentication.
    
    Requirements: 4.1
    """
    app = create_app()
    client = app.test_client()
    
    # Access without authentication
    response = client.get('/signin')
    
    # Should return 200, not redirect
    assert response.status_code == 200
    assert b'Welcome Back' in response.data


def test_signin_redirects_if_logged_in():
    """
    Test that the signin page redirects if user is already logged in.
    
    Requirements: 4.1
    """
    app = create_app()
    client = app.test_client()
    
    # Simulate an authenticated session
    with client.session_transaction() as session:
        session['user_id'] = 1
        session['user_email'] = 'test@example.com'
    
    response = client.get('/signin')
    
    # Should redirect to home
    assert response.status_code == 302
    assert response.location == '/' or response.location.endswith('/')


def test_signin_includes_signup_link():
    """
    Test that the signin page includes a link to sign up.
    
    Requirements: 4.1
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/signin')
    
    # Verify sign up link is present
    assert b"Don't have an account?" in response.data
    assert b'Sign Up' in response.data
    assert b'/signup' in response.data


def test_signin_post_verified_user_success():
    """
    Test that verified user can sign in with correct credentials.
    
    Requirements: 4.2
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='verified@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Attempt to sign in
        response = client.post('/signin', data={
            'email': 'verified@example.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Should redirect to home
        assert response.status_code == 302
        assert '/' in response.location
        
        # Check that session was created
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None
            assert sess.get('user_email') == 'verified@example.com'
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_post_incorrect_password():
    """
    Test that signin rejects incorrect password.
    
    Requirements: 4.3
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='verified@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Attempt to sign in with wrong password
        response = client.post('/signin', data={
            'email': 'verified@example.com',
            'password': 'wrongpassword'
        })
        
        # Should return 401 with error
        assert response.status_code == 401
        assert b'Incorrect email or password' in response.data
        
        # Session should not be created
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_post_nonexistent_email():
    """
    Test that signin rejects nonexistent email.
    
    Requirements: 4.3
    """
    from src.database import Base, engine, db_session
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Attempt to sign in with nonexistent email
        response = client.post('/signin', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        # Should return 401 with error
        assert response.status_code == 401
        assert b'Incorrect email or password' in response.data
        
        # Session should not be created
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_post_unverified_user():
    """
    Test that unverified user cannot sign in.
    
    Requirements: 4.4
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create an unverified test user
        user = User(email='unverified@example.com', is_verified=False)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Attempt to sign in
        response = client.post('/signin', data={
            'email': 'unverified@example.com',
            'password': 'password123'
        })
        
        # Should return 401 with verification error
        assert response.status_code == 401
        assert b'verification' in response.data.lower()
        
        # Session should not be created
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_form_preserves_email_on_error():
    """
    Test that signin form preserves email on authentication error.
    
    Requirements: 4.3
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='test@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Attempt to sign in with wrong password
        response = client.post('/signin', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        # Email should be preserved in the form
        assert b'test@example.com' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_creates_permanent_session():
    """
    Test that signin creates a permanent session.
    
    Requirements: 4.2
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='verified@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Attempt to sign in
        response = client.post('/signin', data={
            'email': 'verified@example.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Check that session is permanent
        with client.session_transaction() as sess:
            assert sess.permanent is True
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signin_success_message():
    """
    Test that successful signin shows success message.
    
    Requirements: 4.2
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='verified@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Initialize session
        with client.session_transaction() as sess:
            pass
        
        # Attempt to sign in
        response = client.post('/signin', data={
            'email': 'verified@example.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Check that flash message was set
        with client.session_transaction() as sess:
            flashes = dict(sess.get('_flashes', []))
            assert any('welcome' in str(msg).lower() or 'signed in' in str(msg).lower() for msg in flashes.values())
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signout_route_exists():
    """
    Test that the signout route exists.
    
    Requirements: 4.5
    """
    app = create_app()
    client = app.test_client()
    
    response = client.get('/signout', follow_redirects=False)
    
    # Should redirect (not 404)
    assert response.status_code == 302


def test_signout_clears_session():
    """
    Test that signout clears the user session.
    
    Requirements: 4.5
    """
    app = create_app()
    client = app.test_client()
    
    # Create a session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_email'] = 'test@example.com'
    
    # Sign out
    response = client.get('/signout', follow_redirects=False)
    
    # Check that session was cleared
    with client.session_transaction() as sess:
        assert sess.get('user_id') is None
        assert sess.get('user_email') is None


def test_signout_redirects_to_home():
    """
    Test that signout redirects to the home page.
    
    Requirements: 4.5
    """
    app = create_app()
    client = app.test_client()
    
    # Create a session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_email'] = 'test@example.com'
    
    # Sign out
    response = client.get('/signout', follow_redirects=False)
    
    # Should redirect to home
    assert response.status_code == 302
    assert '/' in response.location


def test_signout_shows_success_message():
    """
    Test that signout shows a success message.
    
    Requirements: 4.5
    """
    app = create_app()
    client = app.test_client()
    
    # Create a session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_email'] = 'test@example.com'
    
    # Sign out
    response = client.get('/signout', follow_redirects=False)
    
    # Check that flash message was set
    with client.session_transaction() as sess:
        flashes = dict(sess.get('_flashes', []))
        assert any('signed out' in str(msg).lower() for msg in flashes.values())


def test_signout_when_not_logged_in():
    """
    Test that signout works even when user is not logged in.
    
    Requirements: 4.5
    """
    app = create_app()
    client = app.test_client()
    
    # Sign out without being logged in
    response = client.get('/signout', follow_redirects=False)
    
    # Should still redirect to home (graceful handling)
    assert response.status_code == 302
    assert '/' in response.location


def test_signout_prevents_protected_page_access():
    """
    Test that after signout, user cannot access protected pages.
    
    This test verifies that the session termination is effective and
    protected pages are no longer accessible after signing out.
    
    Requirements: 4.5, 5.4
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='verified@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Sign in
        client.post('/signin', data={
            'email': 'verified@example.com',
            'password': 'password123'
        })
        
        # Verify user is logged in
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None
        
        # Sign out
        client.get('/signout')
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
        
        # Note: We would test protected page access here, but those routes
        # haven't been implemented yet (calendar, forum, etc.)
        # This test can be expanded once protected routes are available
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_signout_full_flow():
    """
    Test complete signin -> signout flow.
    
    Requirements: 4.2, 4.5
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a verified test user
        user = User(email='verified@example.com', is_verified=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Sign in
        signin_response = client.post('/signin', data={
            'email': 'verified@example.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Verify signin was successful
        assert signin_response.status_code == 302
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None
            assert sess.get('user_email') == 'verified@example.com'
        
        # Sign out
        signout_response = client.get('/signout', follow_redirects=False)
        
        # Verify signout was successful
        assert signout_response.status_code == 302
        assert '/' in signout_response.location
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
            assert sess.get('user_email') is None
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)
