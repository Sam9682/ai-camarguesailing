"""
Tests for database initialization script.

This module tests the database initialization script to ensure
it creates all required tables correctly and is idempotent.

Requirements: 9.2
"""

import pytest
from sqlalchemy import inspect, text
from src.database import engine, Base
from src.models import User, VerificationToken, Booking, ForumPost, ForumReply


@pytest.fixture(scope='module', autouse=True)
def setup_database():
    """
    Create database tables before running tests.
    
    This fixture ensures that tables are created before any tests run,
    allowing us to test the database structure and initialization.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean up after all tests in this module
    Base.metadata.drop_all(bind=engine)


def test_all_tables_created():
    """
    Test that all expected tables are created in the database.
    
    This test verifies that the database initialization creates
    all five required tables: users, verification_tokens, bookings,
    forum_posts, and forum_replies.
    
    Requirements: 9.2
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = ['users', 'verification_tokens', 'bookings', 'forum_posts', 'forum_replies']
    
    for table in expected_tables:
        assert table in tables, f"Table '{table}' was not created"


def test_users_table_structure():
    """
    Test that the users table has the correct structure.
    
    Requirements: 2.2, 2.5
    """
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('users')}
    
    # Check required columns exist
    assert 'id' in columns
    assert 'email' in columns
    assert 'password_hash' in columns
    assert 'is_verified' in columns
    assert 'created_at' in columns
    assert 'updated_at' in columns
    
    # Check email is unique
    indexes = inspector.get_indexes('users')
    unique_indexes = inspector.get_unique_constraints('users')
    
    # Email should have a unique constraint or unique index
    email_is_unique = any(
        'email' in idx.get('column_names', []) 
        for idx in indexes if idx.get('unique', False)
    ) or any(
        'email' in constraint.get('column_names', [])
        for constraint in unique_indexes
    )
    
    assert email_is_unique, "Email column should have a unique constraint"


def test_verification_tokens_table_structure():
    """
    Test that the verification_tokens table has the correct structure.
    
    Requirements: 3.1, 3.2
    """
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('verification_tokens')}
    
    # Check required columns exist
    assert 'id' in columns
    assert 'user_id' in columns
    assert 'token' in columns
    assert 'expires_at' in columns
    assert 'created_at' in columns
    
    # Check foreign key relationship
    foreign_keys = inspector.get_foreign_keys('verification_tokens')
    assert len(foreign_keys) > 0, "verification_tokens should have a foreign key to users"
    
    user_fk = next((fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None, "user_id should be a foreign key"
    assert user_fk['referred_table'] == 'users', "user_id should reference users table"


def test_bookings_table_structure():
    """
    Test that the bookings table has the correct structure.
    
    Requirements: 7.2, 7.5
    """
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('bookings')}
    
    # Check required columns exist
    assert 'id' in columns
    assert 'user_id' in columns
    assert 'start_date' in columns
    assert 'end_date' in columns
    assert 'status' in columns
    assert 'created_at' in columns
    assert 'updated_at' in columns
    
    # Check foreign key relationship
    foreign_keys = inspector.get_foreign_keys('bookings')
    user_fk = next((fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None, "user_id should be a foreign key"
    assert user_fk['referred_table'] == 'users', "user_id should reference users table"
    
    # Check for date constraint
    check_constraints = inspector.get_check_constraints('bookings')
    has_date_constraint = any(
        'end_date' in constraint.get('sqltext', '').lower() and 
        'start_date' in constraint.get('sqltext', '').lower()
        for constraint in check_constraints
    )
    assert has_date_constraint, "bookings should have a check constraint for end_date > start_date"


def test_forum_posts_table_structure():
    """
    Test that the forum_posts table has the correct structure.
    
    Requirements: 8.2, 8.5
    """
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('forum_posts')}
    
    # Check required columns exist
    assert 'id' in columns
    assert 'user_id' in columns
    assert 'title' in columns
    assert 'content' in columns
    assert 'created_at' in columns
    assert 'updated_at' in columns
    
    # Check foreign key relationship
    foreign_keys = inspector.get_foreign_keys('forum_posts')
    user_fk = next((fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None, "user_id should be a foreign key"


def test_forum_replies_table_structure():
    """
    Test that the forum_replies table has the correct structure.
    
    Requirements: 8.4, 8.5
    """
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('forum_replies')}
    
    # Check required columns exist
    assert 'id' in columns
    assert 'post_id' in columns
    assert 'user_id' in columns
    assert 'content' in columns
    assert 'created_at' in columns
    
    # Check foreign key relationships
    foreign_keys = inspector.get_foreign_keys('forum_replies')
    
    post_fk = next((fk for fk in foreign_keys if 'post_id' in fk['constrained_columns']), None)
    assert post_fk is not None, "post_id should be a foreign key"
    assert post_fk['referred_table'] == 'forum_posts', "post_id should reference forum_posts table"
    
    user_fk = next((fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None, "user_id should be a foreign key"
    assert user_fk['referred_table'] == 'users', "user_id should reference users table"


def test_idempotency():
    """
    Test that running create_all multiple times doesn't cause errors.
    
    This test verifies that the database initialization is idempotent
    and can be run multiple times safely.
    
    Requirements: 9.2
    """
    # Run create_all multiple times
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Verify tables still exist and are correct
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = ['users', 'verification_tokens', 'bookings', 'forum_posts', 'forum_replies']
    
    for table in expected_tables:
        assert table in tables, f"Table '{table}' should still exist after multiple create_all calls"


def test_cascade_deletes():
    """
    Test that foreign key cascade deletes are configured correctly.
    
    This test verifies that when a user is deleted, their related
    records (verification tokens, bookings, posts, replies) are also deleted.
    
    Requirements: 2.2, 7.5, 8.5
    """
    inspector = inspect(engine)
    
    def get_ondelete(fk):
        """Helper to get ondelete option from foreign key."""
        return fk.get('ondelete') or fk.get('options', {}).get('ondelete')
    
    # Check verification_tokens has CASCADE delete
    vt_fks = inspector.get_foreign_keys('verification_tokens')
    user_fk = next((fk for fk in vt_fks if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None
    assert get_ondelete(user_fk) == 'CASCADE', "verification_tokens should have CASCADE delete"
    
    # Check bookings has CASCADE delete
    booking_fks = inspector.get_foreign_keys('bookings')
    user_fk = next((fk for fk in booking_fks if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None
    assert get_ondelete(user_fk) == 'CASCADE', "bookings should have CASCADE delete"
    
    # Check forum_posts has CASCADE delete
    post_fks = inspector.get_foreign_keys('forum_posts')
    user_fk = next((fk for fk in post_fks if 'user_id' in fk['constrained_columns']), None)
    assert user_fk is not None
    assert get_ondelete(user_fk) == 'CASCADE', "forum_posts should have CASCADE delete"
    
    # Check forum_replies has CASCADE delete for both foreign keys
    reply_fks = inspector.get_foreign_keys('forum_replies')
    post_fk = next((fk for fk in reply_fks if 'post_id' in fk['constrained_columns']), None)
    user_fk = next((fk for fk in reply_fks if 'user_id' in fk['constrained_columns']), None)
    
    assert post_fk is not None
    assert get_ondelete(post_fk) == 'CASCADE', "forum_replies should have CASCADE delete for post_id"
    assert user_fk is not None
    assert get_ondelete(user_fk) == 'CASCADE', "forum_replies should have CASCADE delete for user_id"
