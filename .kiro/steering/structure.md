# Project Structure

## Directory Layout

```
camargue-sailing-website/
├── src/                    # Application source code
├── templates/              # Jinja2 HTML templates
├── static/                 # Static assets (CSS, images)
├── tests/                  # Test suite
├── scripts/                # Utility scripts (e.g., init_db.py)
├── conf/                   # Configuration files (e.g., deploy.ini)
├── docs/                   # Documentation and business plans
├── .kiro/                  # Kiro AI assistant configuration
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker services configuration
└── .env                   # Environment variables (not in git)
```

## Source Code Organization (`src/`)

### Core Application Files
- **`app.py`** - Flask application factory, route definitions, error handlers
- **`models.py`** - SQLAlchemy database models (User, Booking, ForumPost, etc.)
- **`database.py`** - Database connection, session management, initialization
- **`config.py`** - Configuration loading from environment variables

### Feature Modules
- **`auth.py`** - Authentication logic (registration, login, verification, decorators)
- **`booking.py`** - Booking management and calendar operations
- **`forum.py`** - Forum post and reply operations
- **`email_service.py`** - Email sending for verification and confirmations

### Test Files
- Test files prefixed with `test_` (e.g., `test_auth.py`, `test_models.py`)
- Located in both `src/` and `tests/` directories

## Templates (`templates/`)

### Public Pages
- `home.html` - Landing page
- `voyages.html` - One-week sailing voyage information
- `camargue.html` - Camargue area information
- `voyage_options.html` - Different voyage options

### Authentication Pages
- `signup.html` - User registration form
- `signin.html` - User login form

### Protected Pages (require authentication)
- `calendar.html` - Booking calendar view
- `book.html` - Booking creation form
- `forum.html` - Forum discussion list
- `new_post.html` - Create new forum post
- `reply.html` - Reply to forum post

### Shared Templates
- `base.html` - Base template with common layout
- `error.html` - Generic error page template

## Static Assets (`static/`)

- **`css/`** - Stylesheets (style.css)
- **`images/`** - AMEL boat photos and other images

## Code Organization Patterns

### Route Definitions
- All routes defined in `app.py` using Flask decorators
- Routes organized by feature: public, authentication, booking, forum
- Protected routes use `@login_required` and `@verified_required` decorators

### Database Models
- All models inherit from `Base` (declarative_base)
- Models include relationships, validators, and helper methods
- Timestamps (created_at, updated_at) on all models

### Business Logic Separation
- Route handlers in `app.py` focus on HTTP concerns (request/response)
- Business logic extracted to feature modules (auth.py, booking.py, forum.py)
- Database operations encapsulated in model methods or feature modules

### Error Handling
- Validation errors raise custom exceptions (RegistrationError, AuthenticationError)
- Database errors caught and rolled back with appropriate user messages
- Error handlers render error.html with context-specific messages

## Testing Structure (`tests/`)

- **Integration tests** - Test full request/response cycle (test_app.py, test_signup_integration.py)
- **Unit tests** - Test individual functions and models (test_auth.py, test_models.py)
- **Property-based tests** - Use Hypothesis for validation testing (test_validation.py)
- **Database tests** - Test error handling and edge cases (test_database_error_handling.py)

## Configuration Files

- **`.env`** - Environment variables (SECRET_KEY, DATABASE_URL, MAIL_* settings)
- **`.env.example`** - Template for required environment variables
- **`docker-compose.yml`** - Defines web and db services with health checks
- **`Dockerfile`** - Python application container definition

## Naming Conventions

- **Python files**: snake_case (e.g., `email_service.py`)
- **Classes**: PascalCase (e.g., `User`, `ForumPost`)
- **Functions/variables**: snake_case (e.g., `register_user`, `user_id`)
- **Templates**: lowercase with underscores (e.g., `new_post.html`)
- **Database tables**: lowercase plural (e.g., `users`, `forum_posts`)
- **Routes**: lowercase with hyphens in URLs (e.g., `/voyage-options`)
