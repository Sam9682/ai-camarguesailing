# Database Scripts

This directory contains scripts for managing the Camargue Sailing website database.

## Database Initialization

### init_db.py

Creates all database tables from the SQLAlchemy models defined in `src/models.py`.

**Features:**
- Creates all required tables (users, verification_tokens, bookings, forum_posts, forum_replies)
- Idempotent - can be run multiple times safely without errors
- Verifies database connection before creating tables
- Provides detailed logging of the initialization process

**Usage:**

```bash
# Activate virtual environment
source venv/bin/activate

# Run the initialization script
python scripts/init_db.py
```

**Requirements:**
- PostgreSQL database must be running
- Database connection string must be configured in `.env` file
- All Python dependencies must be installed (`pip install -r requirements.txt`)

**Environment Variables:**

The script uses the following environment variables from `.env`:
- `DATABASE_URL` - PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/dbname`)
- `SECRET_KEY` - Flask secret key
- `MAIL_USERNAME` - Email service username
- `MAIL_PASSWORD` - Email service password

**Output:**

The script will:
1. Test the database connection
2. Create all tables if they don't exist
3. Verify all expected tables are present
4. Print success/error messages with detailed logging

**Exit Codes:**
- `0` - Success
- `1` - Failure (check logs for details)

**Example Output:**

```
============================================================
Camargue Sailing Website - Database Initialization
============================================================
2024-02-14 15:37:46,761 - __main__ - INFO - Starting database initialization...
2024-02-14 15:37:46,761 - __main__ - INFO - Database URL: postgresql://camargue_user:***@localhost:5432/camargue_sailing
2024-02-14 15:37:46,761 - __main__ - INFO - Testing database connection...
2024-02-14 15:37:46,762 - __main__ - INFO - ✓ Database connection successful
2024-02-14 15:37:46,762 - __main__ - INFO - Creating database tables...
2024-02-14 15:37:46,778 - __main__ - INFO - ✓ Database tables created successfully:
2024-02-14 15:37:46,778 - __main__ - INFO -   - users
2024-02-14 15:37:46,778 - __main__ - INFO -   - verification_tokens
2024-02-14 15:37:46,778 - __main__ - INFO -   - bookings
2024-02-14 15:37:46,778 - __main__ - INFO -   - forum_posts
2024-02-14 15:37:46,778 - __main__ - INFO -   - forum_replies
2024-02-14 15:37:46,778 - __main__ - INFO - ✓ All expected tables are present
============================================================
✓ Database initialization completed successfully
============================================================
```

## Docker Usage

If using Docker Compose, ensure the database container is running:

```bash
# Start the database
docker-compose up -d db

# Wait for database to be ready
sleep 5

# Run initialization script
source venv/bin/activate
python scripts/init_db.py
```

## Troubleshooting

**Error: "DATABASE_URL environment variable is required"**
- Ensure `.env` file exists and contains `DATABASE_URL`
- Copy `.env.example` to `.env` and update values if needed

**Error: "Failed to connect to database"**
- Verify PostgreSQL is running: `docker ps | grep postgres`
- Check database credentials in `.env`
- Ensure database exists: `docker exec <container> psql -U <user> -l`

**Error: "ModuleNotFoundError: No module named 'sqlalchemy'"**
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Testing

The database initialization is tested in `tests/test_init_db.py`:

```bash
# Run initialization tests
source venv/bin/activate
python -m pytest tests/test_init_db.py -v
```

Tests verify:
- All tables are created
- Table structures match model definitions
- Foreign key relationships are correct
- Check constraints are in place
- Cascade deletes are configured
- Idempotency (can run multiple times safely)
