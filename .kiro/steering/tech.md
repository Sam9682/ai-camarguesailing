# Technology Stack

## Core Framework
- **Flask 3.0.0** - Web framework with Jinja2 templating
- **Python 3.11+** - Primary language

## Database
- **PostgreSQL 15+** - Primary database
- **SQLAlchemy 2.0.23** - ORM for database models
- **psycopg 3.3.2** - PostgreSQL adapter

## Authentication & Security
- **Flask-Bcrypt 1.0.1** - Password hashing
- **Werkzeug 3.0.1** - Security utilities
- Session-based authentication with secure cookies

## Email
- **Flask-Mail 0.9.1** - Email sending for verification and confirmations

## Testing
- **pytest 7.4.3** - Test framework
- **pytest-flask 1.3.0** - Flask testing utilities
- **hypothesis 6.92.1** - Property-based testing
- **freezegun 1.4.0** - Time mocking for tests
- **responses 0.24.1** - HTTP mocking

## Configuration
- **python-dotenv 1.0.0** - Environment variable management

## Deployment
- **Docker & Docker Compose** - Containerization
- PostgreSQL runs in separate container with health checks

## Common Commands

### Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
flask run

# Initialize database
python scripts/init_db.py
```

### Testing
```bash
# Run all tests
pytest

# Run with property-based testing iterations
pytest --hypothesis-iterations=1000

# Run specific test file
pytest tests/test_auth.py
```

### Docker
```bash
# Build and start containers
docker-compose up --build

# Stop containers
docker-compose down

# View logs
docker-compose logs -f web
```

## Architecture Patterns

### Database Session Management
- Uses scoped sessions for thread-safety
- Sessions automatically closed via `@app.teardown_appcontext`
- Connection pooling with pre-ping and recycling

### Configuration
- Environment-based configuration via `.env` file
- Config class in `src/config.py` validates required variables
- Separate config for development/production

### Error Handling
- Custom error handlers for 401, 403, 404, 500
- Database rollback on errors
- Graceful degradation for non-critical failures (e.g., email sending)
