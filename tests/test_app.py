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
