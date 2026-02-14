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



def test_calendar_route_requires_authentication():
    """
    Test that the calendar route requires authentication.
    
    Requirements: 5.1, 6.1
    """
    app = create_app()
    client = app.test_client()
    
    # Try to access calendar without authentication
    response = client.get('/calendar', follow_redirects=False)
    
    # Should redirect to signin
    assert response.status_code == 302
    assert '/signin' in response.location


def test_calendar_route_requires_verification():
    """
    Test that the calendar route requires email verification.
    
    Requirements: 3.5, 6.1
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
        user_id = user.id
        
        # Simulate authenticated but unverified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'unverified@example.com'
        
        # Try to access calendar
        response = client.get('/calendar', follow_redirects=False)
        
        # Should redirect to home with error message
        assert response.status_code == 302
        assert '/' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_route_renders_for_verified_user():
    """
    Test that the calendar route renders successfully for verified users.
    
    Requirements: 6.1
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar
        response = client.get('/calendar')
        
        # Should render successfully
        assert response.status_code == 200
        assert b'Sailing Calendar' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_displays_current_year():
    """
    Test that the calendar displays the current year.
    
    Requirements: 6.1
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import datetime
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar
        response = client.get('/calendar')
        
        # Should display current year
        current_year = datetime.now().year
        assert str(current_year).encode() in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_displays_booked_periods():
    """
    Test that the calendar displays booked periods.
    
    Requirements: 6.2
    """
    from src.database import Base, engine, db_session
    from src.models import User, Booking
    from datetime import date, datetime
    
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
        user_id = user.id
        
        # Create a booking for current year
        current_year = datetime.now().year
        booking = Booking(
            user_id=user_id,
            start_date=date(current_year, 6, 1),
            end_date=date(current_year, 6, 8),
            status='confirmed'
        )
        db_session.add(booking)
        db_session.commit()
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar
        response = client.get('/calendar')
        
        # Should display the booking
        assert response.status_code == 200
        assert b'Booked Periods' in response.data
        assert str(current_year).encode() in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_shows_no_bookings_message():
    """
    Test that the calendar shows appropriate message when no bookings exist.
    
    Requirements: 6.1, 6.3
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar (no bookings exist)
        response = client.get('/calendar')
        
        # Should show no bookings message
        assert response.status_code == 200
        assert b'No bookings found' in response.data or b'All periods are currently available' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_includes_navigation_links():
    """
    Test that the calendar includes navigation links back to other pages.
    
    Requirements: 6.1
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar
        response = client.get('/calendar')
        
        # Should include navigation links
        assert response.status_code == 200
        assert b'Back to Home' in response.data or b'Home' in response.data
        assert b'Voyage' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_displays_booking_status():
    """
    Test that the calendar displays booking status (confirmed/cancelled).
    
    Requirements: 6.2
    """
    from src.database import Base, engine, db_session
    from src.models import User, Booking
    from datetime import date, datetime
    
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
        user_id = user.id
        
        # Create bookings with different statuses
        current_year = datetime.now().year
        booking1 = Booking(
            user_id=user_id,
            start_date=date(current_year, 6, 1),
            end_date=date(current_year, 6, 8),
            status='confirmed'
        )
        booking2 = Booking(
            user_id=user_id,
            start_date=date(current_year, 7, 1),
            end_date=date(current_year, 7, 8),
            status='cancelled'
        )
        db_session.add(booking1)
        db_session.add(booking2)
        db_session.commit()
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar
        response = client.get('/calendar')
        
        # Should display booking statuses
        assert response.status_code == 200
        assert b'confirmed' in response.data.lower() or b'Confirmed' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_calendar_legend_shows_availability():
    """
    Test that the calendar includes a legend showing available/booked indicators.
    
    Requirements: 6.2, 6.3
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access calendar
        response = client.get('/calendar')
        
        # Should include legend
        assert response.status_code == 200
        assert b'Available' in response.data
        assert b'Booked' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)



def test_book_route_requires_authentication():
    """
    Test that the booking route requires authentication.
    
    Requirements: 5.1, 7.1
    """
    app = create_app()
    client = app.test_client()
    
    # Try to access booking page without authentication
    response = client.get('/book', follow_redirects=False)
    
    # Should redirect to signin
    assert response.status_code == 302
    assert '/signin' in response.location


def test_book_route_requires_verification():
    """
    Test that the booking route requires email verification.
    
    Requirements: 3.5, 7.1
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
        user_id = user.id
        
        # Simulate authenticated but unverified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'unverified@example.com'
        
        # Try to access booking page
        response = client.get('/book', follow_redirects=False)
        
        # Should redirect to home with error message
        assert response.status_code == 302
        assert '/' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_page_get():
    """
    Test that the booking page displays the booking form.
    
    Requirements: 7.1
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access booking page
        response = client.get('/book')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify booking form is present
        assert b'Book Your Sailing Voyage' in response.data
        assert b'Start Date' in response.data
        assert b'End Date' in response.data
        assert b'Create Booking' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_page_includes_date_inputs():
    """
    Test that the booking page includes date input fields.
    
    Requirements: 7.1
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access booking page
        response = client.get('/book')
        
        # Verify date input fields are present
        assert b'type="date"' in response.data
        assert b'name="start_date"' in response.data
        assert b'name="end_date"' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_success():
    """
    Test that booking creation succeeds with valid dates.
    
    Requirements: 7.2
    """
    from src.database import Base, engine, db_session
    from src.models import User, Booking
    from datetime import date, timedelta
    from unittest.mock import patch
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with future dates
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        # Mock send_booking_confirmation to avoid email sending
        with patch('src.email_service.send_booking_confirmation') as mock_send:
            mock_send.return_value = True
            
            # Submit booking
            response = client.post('/book', data={
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }, follow_redirects=False)
        
        # Should redirect to calendar
        assert response.status_code == 302
        assert '/calendar' in response.location
        
        # Verify booking was created in database
        booking = db_session.query(Booking).filter_by(user_id=user_id).first()
        assert booking is not None
        assert booking.start_date == start_date
        assert booking.end_date == end_date
        assert booking.status == 'confirmed'
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_missing_dates():
    """
    Test that booking creation fails with missing dates.
    
    Requirements: 7.2
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Submit booking without dates
        response = client.post('/book', data={})
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'required' in response.data.lower()
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_invalid_date_format():
    """
    Test that booking creation fails with invalid date format.
    
    Requirements: 7.2
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Submit booking with invalid date format
        response = client.post('/book', data={
            'start_date': 'invalid-date',
            'end_date': '2024-12-31'
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'Invalid date format' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_end_before_start():
    """
    Test that booking creation fails when end date is before start date.
    
    Requirements: 7.2
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import date, timedelta
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with end date before start date
        start_date = date.today() + timedelta(days=30)
        end_date = start_date - timedelta(days=1)
        
        # Submit booking
        response = client.post('/book', data={
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'End date must be after start date' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_overlapping_booking():
    """
    Test that booking creation fails when dates overlap with existing booking.
    
    Requirements: 7.3
    """
    from src.database import Base, engine, db_session
    from src.models import User, Booking
    from datetime import date, timedelta
    
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
        user_id = user.id
        
        # Create an existing booking
        existing_start = date.today() + timedelta(days=30)
        existing_end = existing_start + timedelta(days=7)
        existing_booking = Booking(
            user_id=user_id,
            start_date=existing_start,
            end_date=existing_end,
            status='confirmed'
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Try to create overlapping booking
        overlap_start = existing_start + timedelta(days=3)
        overlap_end = overlap_start + timedelta(days=7)
        
        # Submit booking
        response = client.post('/book', data={
            'start_date': overlap_start.strftime('%Y-%m-%d'),
            'end_date': overlap_end.strftime('%Y-%m-%d')
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'overlap' in response.data.lower() or b'not available' in response.data.lower()
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_success_message():
    """
    Test that successful booking shows success message.
    
    Requirements: 7.2
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import date, timedelta
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with future dates
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        # Initialize session for flash messages
        with client.session_transaction() as sess:
            pass
        
        # Submit booking
        response = client.post('/book', data={
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }, follow_redirects=False)
        
        # Check that flash message was set
        with client.session_transaction() as sess:
            flashes = dict(sess.get('_flashes', []))
            assert any('success' in str(msg).lower() or 'created' in str(msg).lower() for msg in flashes.values())
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_form_preserves_dates_on_error():
    """
    Test that booking form preserves dates on validation error.
    
    Requirements: 7.2
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import date, timedelta
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with end date before start date
        start_date = date.today() + timedelta(days=30)
        end_date = start_date - timedelta(days=1)
        
        # Submit booking
        response = client.post('/book', data={
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })
        
        # Dates should be preserved in the form
        assert start_date.strftime('%Y-%m-%d').encode() in response.data
        assert end_date.strftime('%Y-%m-%d').encode() in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_page_includes_calendar_link():
    """
    Test that the booking page includes a link to view the calendar.
    
    Requirements: 7.1
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access booking page
        response = client.get('/book')
        
        # Verify calendar link is present
        assert b'View Calendar' in response.data
        assert b'/calendar' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_page_includes_voyage_info():
    """
    Test that the booking page includes information about voyages.
    
    Requirements: 7.1
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Access booking page
        response = client.get('/book')
        
        # Verify voyage information is present
        assert b'one week' in response.data.lower() or b'7 days' in response.data.lower()
        assert b'confirmation email' in response.data.lower()
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)



def test_book_post_sends_confirmation_email():
    """
    Test that booking creation sends a confirmation email.
    
    This test verifies that send_booking_confirmation() is called
    after a successful booking is created with both booking and user objects.
    
    Requirements: 7.6
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import date, timedelta
    from unittest.mock import patch
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with future dates
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        # Mock send_booking_confirmation at the email_service module level
        with patch('src.email_service.send_booking_confirmation') as mock_send:
            mock_send.return_value = True
            
            # Submit booking
            response = client.post('/book', data={
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }, follow_redirects=False)
            
            # Verify send_booking_confirmation was called
            assert mock_send.called
            assert mock_send.call_count == 1
            
            # Verify it was called with 2 arguments (booking and user)
            call_args = mock_send.call_args[0]
            assert len(call_args) == 2
            
            # Verify the arguments are the right types
            booking_arg, user_arg = call_args
            assert booking_arg.__class__.__name__ == 'Booking'
            assert user_arg.__class__.__name__ == 'User'
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_email_failure_does_not_fail_booking():
    """
    Test that email sending failure does not prevent booking creation.
    
    This test verifies that if send_booking_confirmation() fails,
    the booking is still created and the user is notified.
    
    Requirements: 7.6
    """
    from src.database import Base, engine, db_session
    from src.models import User, Booking
    from datetime import date, timedelta
    from unittest.mock import patch
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with future dates
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        # Mock send_booking_confirmation to raise an exception
        with patch('src.email_service.send_booking_confirmation') as mock_send:
            mock_send.side_effect = Exception("SMTP connection failed")
            
            # Submit booking
            response = client.post('/book', data={
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }, follow_redirects=False)
            
            # Should still redirect to calendar (booking succeeded)
            assert response.status_code == 302
            assert '/calendar' in response.location
            
            # Verify booking was created in database despite email failure
            booking = db_session.query(Booking).filter_by(user_id=user_id).first()
            assert booking is not None
            assert booking.start_date == start_date
            assert booking.end_date == end_date
            assert booking.status == 'confirmed'
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_email_failure_shows_warning():
    """
    Test that email sending failure shows a warning message to the user.
    
    This test verifies that if send_booking_confirmation() fails,
    the user sees a warning message indicating the email could not be sent.
    
    Requirements: 7.6
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import date, timedelta
    from unittest.mock import patch
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with future dates
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        # Mock send_booking_confirmation to raise an exception
        with patch('src.email_service.send_booking_confirmation') as mock_send:
            mock_send.side_effect = Exception("SMTP connection failed")
            
            # Submit booking and follow redirects to see flash messages
            response = client.post('/book', data={
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }, follow_redirects=True)
            
            # Verify warning message is shown
            assert b'Booking created successfully' in response.data
            assert b'could not send the confirmation email' in response.data
            assert b'contact support' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_book_post_email_success_shows_success_message():
    """
    Test that successful email sending shows a success message.
    
    This test verifies that when send_booking_confirmation() succeeds,
    the user sees a success message indicating the email was sent.
    
    Requirements: 7.6
    """
    from src.database import Base, engine, db_session
    from src.models import User
    from datetime import date, timedelta
    from unittest.mock import patch
    
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
        user_id = user.id
        
        # Simulate authenticated and verified session
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_email'] = 'verified@example.com'
        
        # Create booking with future dates
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        # Mock send_booking_confirmation to succeed
        with patch('src.email_service.send_booking_confirmation') as mock_send:
            mock_send.return_value = True
            
            # Submit booking and follow redirects to see flash messages
            response = client.post('/book', data={
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }, follow_redirects=True)
            
            # Verify success message is shown
            assert b'Booking created successfully' in response.data
            assert b'confirmation email has been sent' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_requires_authentication():
    """
    Test that the forum page requires authentication.
    
    Requirements: 8.6
    """
    from src.database import Base, engine, db_session
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Try to access forum without authentication
        response = client.get('/forum', follow_redirects=False)
        
        # Should redirect to signin
        assert response.status_code == 302
        assert '/signin' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_requires_verification():
    """
    Test that the forum page requires email verification.
    
    Requirements: 8.6
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
        user_id = user.id
        
        # Simulate an unverified user session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'unverified@example.com'
        
        # Try to access forum
        response = client.get('/forum', follow_redirects=False)
        
        # Should redirect to home with error message
        assert response.status_code == 302
        assert '/' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_displays_posts():
    """
    Test that the forum page displays all posts with author and timestamp.
    
    Requirements: 8.1, 8.3
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    from datetime import datetime
    
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
        user_id = user.id
        
        # Create test forum posts
        post1 = ForumPost(
            user_id=user_id,
            title='First Post',
            content='This is the first post content'
        )
        post2 = ForumPost(
            user_id=user_id,
            title='Second Post',
            content='This is the second post content'
        )
        db_session.add(post1)
        db_session.add(post2)
        db_session.commit()
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access forum page
        response = client.get('/forum')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify forum content is present
        assert b'Discussion Forum' in response.data
        assert b'First Post' in response.data
        assert b'Second Post' in response.data
        assert b'This is the first post content' in response.data
        assert b'This is the second post content' in response.data
        
        # Verify author is displayed
        assert b'verified@example.com' in response.data
        
        # Verify timestamp is displayed (check for date format elements)
        assert b'2024' in response.data or b'2025' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_displays_replies():
    """
    Test that the forum page displays replies to posts.
    
    Requirements: 8.1, 8.3
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost, ForumReply
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create verified test users
        user1 = User(email='user1@example.com', is_verified=True)
        user1.set_password('password123')
        user2 = User(email='user2@example.com', is_verified=True)
        user2.set_password('password123')
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        user1_id = user1.id
        user2_id = user2.id
        
        # Create a forum post
        post = ForumPost(
            user_id=user1_id,
            title='Post with Replies',
            content='This post has replies'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Create replies
        reply1 = ForumReply(
            post_id=post_id,
            user_id=user2_id,
            content='This is the first reply'
        )
        reply2 = ForumReply(
            post_id=post_id,
            user_id=user1_id,
            content='This is the second reply'
        )
        db_session.add(reply1)
        db_session.add(reply2)
        db_session.commit()
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user1_id
            session['user_email'] = 'user1@example.com'
        
        # Access forum page
        response = client.get('/forum')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify post and replies are displayed
        assert b'Post with Replies' in response.data
        assert b'This post has replies' in response.data
        assert b'This is the first reply' in response.data
        assert b'This is the second reply' in response.data
        
        # Verify reply authors are displayed
        assert b'user1@example.com' in response.data
        assert b'user2@example.com' in response.data
        
        # Verify replies section is present
        assert b'Replies' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_empty_state():
    """
    Test that the forum page displays appropriate message when no posts exist.
    
    Requirements: 8.1
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access forum page
        response = client.get('/forum')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify empty state message is displayed
        assert b'No posts yet' in response.data
        assert b'Be the first to start a discussion' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_includes_create_post_link():
    """
    Test that the forum page includes a link to create new posts.
    
    Requirements: 8.1
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access forum page
        response = client.get('/forum')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify create post link is present
        assert b'Create New Post' in response.data or b'Create First Post' in response.data
        assert b'/forum/new' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_forum_page_post_ordering():
    """
    Test that forum posts are ordered by creation date (newest first).
    
    Requirements: 8.1
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    from datetime import datetime, timedelta
    
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
        user_id = user.id
        
        # Create posts with different timestamps
        old_post = ForumPost(
            user_id=user_id,
            title='Old Post',
            content='This is an old post'
        )
        old_post.created_at = datetime.utcnow() - timedelta(days=2)
        
        new_post = ForumPost(
            user_id=user_id,
            title='New Post',
            content='This is a new post'
        )
        new_post.created_at = datetime.utcnow()
        
        db_session.add(old_post)
        db_session.add(new_post)
        db_session.commit()
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access forum page
        response = client.get('/forum')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify both posts are present
        assert b'Old Post' in response.data
        assert b'New Post' in response.data
        
        # Verify new post appears before old post (by checking byte positions)
        new_post_pos = response.data.find(b'New Post')
        old_post_pos = response.data.find(b'Old Post')
        assert new_post_pos < old_post_pos, "New post should appear before old post"
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_page_get():
    """
    Test that the new post page displays the post creation form.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access new post page
        response = client.get('/forum/new')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify form elements are present
        assert b'Create New Post' in response.data
        assert b'Post Title' in response.data
        assert b'Post Content' in response.data
        assert b'Create Post' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_page_requires_authentication():
    """
    Test that the new post page requires authentication.
    
    Requirements: 8.2, 8.6
    """
    app = create_app()
    client = app.test_client()
    
    # Access new post page without authentication
    response = client.get('/forum/new', follow_redirects=False)
    
    # Should redirect to signin
    assert response.status_code == 302
    assert '/signin' in response.location


def test_new_post_page_requires_verification():
    """
    Test that the new post page requires email verification.
    
    Requirements: 8.2, 8.6
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
        user_id = user.id
        
        # Simulate an authenticated but unverified session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'unverified@example.com'
        
        # Access new post page
        response = client.get('/forum/new', follow_redirects=False)
        
        # Should redirect to home or show error
        assert response.status_code == 302
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_post_success():
    """
    Test that verified user can create a new post successfully.
    
    Requirements: 8.2
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit new post
        response = client.post('/forum/new', data={
            'title': 'Test Post Title',
            'content': 'This is the content of my test post.'
        }, follow_redirects=False)
        
        # Should redirect to forum
        assert response.status_code == 302
        assert '/forum' in response.location
        
        # Verify post was created in database
        post = db_session.query(ForumPost).filter_by(title='Test Post Title').first()
        assert post is not None
        assert post.content == 'This is the content of my test post.'
        assert post.user_id == user_id
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_post_empty_title():
    """
    Test that new post creation rejects empty title.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit new post with empty title
        response = client.post('/forum/new', data={
            'title': '',
            'content': 'This is the content of my test post.'
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'Title is required' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_post_empty_content():
    """
    Test that new post creation rejects empty content.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit new post with empty content
        response = client.post('/forum/new', data={
            'title': 'Test Post Title',
            'content': ''
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'Content is required' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_form_preserves_data_on_error():
    """
    Test that new post form preserves data on validation error.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit new post with empty content
        response = client.post('/forum/new', data={
            'title': 'Test Post Title',
            'content': ''
        })
        
        # Title should be preserved in the form
        assert b'Test Post Title' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_success_message():
    """
    Test that successful post creation shows success message.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit new post
        response = client.post('/forum/new', data={
            'title': 'Test Post Title',
            'content': 'This is the content of my test post.'
        }, follow_redirects=True)
        
        # Should show success message
        assert b'Post created successfully!' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_redirects_to_forum():
    """
    Test that successful post creation redirects to forum page.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit new post
        response = client.post('/forum/new', data={
            'title': 'Test Post Title',
            'content': 'This is the content of my test post.'
        }, follow_redirects=True)
        
        # Should be on forum page
        assert response.status_code == 200
        assert b'Discussion Forum' in response.data
        assert b'Test Post Title' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_new_post_includes_back_link():
    """
    Test that new post page includes a link back to forum.
    
    Requirements: 8.2
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access new post page
        response = client.get('/forum/new')
        
        # Verify back link is present
        assert b'Back to Forum' in response.data
        assert b'/forum' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_get_requires_authentication():
    """
    Test that the reply route (GET) requires authentication.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Try to access reply page without authentication
        response = client.get('/forum/1/reply', follow_redirects=False)
        
        # Should redirect to signin
        assert response.status_code == 302
        assert '/signin' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_get_requires_verification():
    """
    Test that the reply route (GET) requires email verification.
    
    Requirements: 8.4
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
        user_id = user.id
        
        # Simulate an authenticated but unverified session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'unverified@example.com'
        
        # Try to access reply page
        response = client.get('/forum/1/reply', follow_redirects=False)
        
        # Should redirect (verification required)
        assert response.status_code == 302
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_get_displays_form():
    """
    Test that the reply route (GET) displays the reply form.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access reply page
        response = client.get(f'/forum/{post_id}/reply')
        
        # Verify successful response
        assert response.status_code == 200
        
        # Verify reply form is present
        assert b'Reply to Post' in response.data
        assert b'Your Reply' in response.data
        assert b'Post Reply' in response.data
        
        # Verify original post is displayed
        assert b'Test Post' in response.data
        assert b'This is a test post.' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_get_nonexistent_post():
    """
    Test that the reply route (GET) handles nonexistent posts.
    
    Requirements: 8.4
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Try to access reply page for nonexistent post
        response = client.get('/forum/99999/reply', follow_redirects=False)
        
        # Should redirect to forum
        assert response.status_code == 302
        assert '/forum' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_post_creates_reply():
    """
    Test that the reply route (POST) creates a reply successfully.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost, ForumReply
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit reply
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': 'This is my reply to the post.'
        }, follow_redirects=False)
        
        # Should redirect to forum
        assert response.status_code == 302
        assert '/forum' in response.location
        
        # Verify reply was created in database
        reply = db_session.query(ForumReply).filter_by(post_id=post_id).first()
        assert reply is not None
        assert reply.content == 'This is my reply to the post.'
        assert reply.user_id == user_id
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_post_empty_content():
    """
    Test that the reply route (POST) rejects empty content.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit reply with empty content
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': ''
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'Reply content is required' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_post_whitespace_only_content():
    """
    Test that the reply route (POST) rejects whitespace-only content.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit reply with whitespace-only content
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': '   \n\t  '
        })
        
        # Should return 400 with error
        assert response.status_code == 400
        assert b'cannot be empty' in response.data or b'required' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_post_nonexistent_post():
    """
    Test that the reply route (POST) handles nonexistent posts.
    
    Requirements: 8.4
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
        user_id = user.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Try to submit reply to nonexistent post
        response = client.post('/forum/99999/reply', data={
            'content': 'This is my reply.'
        }, follow_redirects=False)
        
        # Should redirect to forum
        assert response.status_code == 302
        assert '/forum' in response.location
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_post_redirects_to_forum():
    """
    Test that successful reply creation redirects to forum page.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit reply
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': 'This is my reply.'
        }, follow_redirects=True)
        
        # Should be on forum page
        assert response.status_code == 200
        assert b'Discussion Forum' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_post_shows_success_message():
    """
    Test that successful reply creation shows a success message.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Submit reply
        response = client.post(f'/forum/{post_id}/reply', data={
            'content': 'This is my reply.'
        }, follow_redirects=True)
        
        # Should show success message
        assert b'Reply posted successfully' in response.data or b'success' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_reply_route_includes_cancel_link():
    """
    Test that reply page includes a cancel link back to forum.
    
    Requirements: 8.4
    """
    from src.database import Base, engine, db_session
    from src.models import User, ForumPost
    
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
        user_id = user.id
        
        # Create a test post
        post = ForumPost(
            user_id=user_id,
            title='Test Post',
            content='This is a test post.'
        )
        db_session.add(post)
        db_session.commit()
        post_id = post.id
        
        # Simulate an authenticated session
        with client.session_transaction() as session:
            session['user_id'] = user_id
            session['user_email'] = 'verified@example.com'
        
        # Access reply page
        response = client.get(f'/forum/{post_id}/reply')
        
        # Verify cancel link is present
        assert b'Cancel' in response.data
        assert b'/forum' in response.data
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_404_error_handler():
    """
    Test that 404 errors are handled correctly.
    
    This test verifies that accessing a non-existent page returns
    a 404 status code and displays the error page.
    """
    app = create_app()
    client = app.test_client()
    
    # Access a non-existent page
    response = client.get('/nonexistent-page')
    
    # Should return 404
    assert response.status_code == 404
    
    # Should display error page
    assert b'404' in response.data
    assert b'Page Not Found' in response.data
    assert b'does not exist' in response.data


def test_404_error_includes_home_link():
    """
    Test that 404 error page includes a link to home.
    
    This test verifies that the error page provides navigation
    back to the home page.
    """
    app = create_app()
    client = app.test_client()
    
    # Access a non-existent page
    response = client.get('/nonexistent-page')
    
    # Should include home link
    assert b'Go to Home' in response.data
    assert b'href="/"' in response.data


def test_500_error_handler():
    """
    Test that 500 errors are handled correctly.
    
    This test verifies that internal server errors return
    a 500 status code and display the error page.
    """
    app = create_app()
    client = app.test_client()
    
    # Create a route that raises an exception
    @app.route('/test-500')
    def test_500():
        raise Exception('Test internal server error')
    
    # Access the route
    response = client.get('/test-500')
    
    # Should return 500
    assert response.status_code == 500
    
    # Should display error page
    assert b'500' in response.data
    assert b'Internal Server Error' in response.data
    assert b'unexpected error' in response.data


def test_500_error_includes_home_link():
    """
    Test that 500 error page includes a link to home.
    
    This test verifies that the error page provides navigation
    back to the home page.
    """
    app = create_app()
    client = app.test_client()
    
    # Create a route that raises an exception
    @app.route('/test-500')
    def test_500():
        raise Exception('Test internal server error')
    
    # Access the route
    response = client.get('/test-500')
    
    # Should include home link
    assert b'Go to Home' in response.data
    assert b'href="/"' in response.data


def test_403_error_handler():
    """
    Test that 403 errors are handled correctly.
    
    This test verifies that forbidden access returns
    a 403 status code and displays the error page.
    """
    from flask import abort
    
    app = create_app()
    client = app.test_client()
    
    # Create a route that returns 403
    @app.route('/test-403')
    def test_403():
        abort(403)
    
    # Access the route
    response = client.get('/test-403')
    
    # Should return 403
    assert response.status_code == 403
    
    # Should display error page
    assert b'403' in response.data
    assert b'Forbidden' in response.data
    assert b'permission' in response.data


def test_403_error_includes_home_link():
    """
    Test that 403 error page includes a link to home.
    
    This test verifies that the error page provides navigation
    back to the home page.
    """
    from flask import abort
    
    app = create_app()
    client = app.test_client()
    
    # Create a route that returns 403
    @app.route('/test-403')
    def test_403():
        abort(403)
    
    # Access the route
    response = client.get('/test-403')
    
    # Should include home link
    assert b'Go to Home' in response.data
    assert b'href="/"' in response.data


def test_401_error_handler():
    """
    Test that 401 errors are handled correctly.
    
    This test verifies that unauthorized access returns
    a 401 status code and displays the error page.
    """
    from flask import abort
    
    app = create_app()
    client = app.test_client()
    
    # Create a route that returns 401
    @app.route('/test-401')
    def test_401():
        abort(401)
    
    # Access the route
    response = client.get('/test-401')
    
    # Should return 401
    assert response.status_code == 401
    
    # Should display error page
    assert b'401' in response.data
    assert b'Unauthorized' in response.data
    assert b'Authentication' in response.data


def test_401_error_includes_signin_link():
    """
    Test that 401 error page includes a link to sign in.
    
    This test verifies that the error page provides navigation
    to the sign in page for authentication.
    """
    from flask import abort
    
    app = create_app()
    client = app.test_client()
    
    # Create a route that returns 401
    @app.route('/test-401')
    def test_401():
        abort(401)
    
    # Access the route
    response = client.get('/test-401')
    
    # Should include sign in link
    assert b'Sign In' in response.data
    assert b'/signin' in response.data


def test_401_error_includes_home_link():
    """
    Test that 401 error page includes a link to home.
    
    This test verifies that the error page provides navigation
    back to the home page.
    """
    from flask import abort
    
    app = create_app()
    client = app.test_client()
    
    # Create a route that returns 401
    @app.route('/test-401')
    def test_401():
        abort(401)
    
    # Access the route
    response = client.get('/test-401')
    
    # Should include home link
    assert b'Go to Home' in response.data
    assert b'href="/"' in response.data


def test_error_pages_use_base_template():
    """
    Test that error pages extend the base template.
    
    This test verifies that error pages include the standard
    navigation and layout from the base template.
    """
    app = create_app()
    client = app.test_client()
    
    # Access a non-existent page
    response = client.get('/nonexistent-page')
    
    # Should include base template elements
    assert b'Camargue Sailing' in response.data
    assert b'Home' in response.data
    assert b'Voyages' in response.data


def test_500_error_rolls_back_database():
    """
    Test that 500 errors rollback database transactions.
    
    This test verifies that when a 500 error occurs, any pending
    database transactions are rolled back to maintain data integrity.
    """
    from src.database import Base, engine, db_session
    from src.models import User
    
    # Set up database
    Base.metadata.create_all(bind=engine)
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Create a route that modifies database then raises exception
        @app.route('/test-500-db')
        def test_500_db():
            user = User(email='test@example.com', is_verified=False)
            user.set_password('password123')
            db_session.add(user)
            # Don't commit - let the error handler rollback
            raise Exception('Test database rollback')
        
        # Access the route
        response = client.get('/test-500-db')
        
        # Should return 500
        assert response.status_code == 500
        
        # User should not be in database (transaction rolled back)
        user = db_session.query(User).filter_by(email='test@example.com').first()
        assert user is None
        
    finally:
        # Clean up
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


def test_error_handler_with_different_methods():
    """
    Test that error handlers work with different HTTP methods.
    
    This test verifies that error handlers are triggered correctly
    for POST, PUT, DELETE, etc., not just GET requests.
    """
    app = create_app()
    client = app.test_client()
    
    # Test 404 with POST
    response = client.post('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data
    
    # Test 404 with PUT
    response = client.put('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data
    
    # Test 404 with DELETE
    response = client.delete('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data
