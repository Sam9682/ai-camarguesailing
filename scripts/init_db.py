#!/usr/bin/env python3
"""
Database initialization script for Camargue Sailing website.

This script creates all database tables from the SQLAlchemy models.
It is idempotent - can be run multiple times safely without errors.

Usage:
    python scripts/init_db.py

Requirements: 9.2
"""

import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import engine, Base
from src.models import User, VerificationToken, Booking, ForumPost, ForumReply

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """
    Initialize the database by creating all tables.
    
    This function is idempotent - it will only create tables that don't exist.
    Existing tables will not be modified or dropped.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Database URL: {engine.url}")
        
        # Test database connection
        logger.info("Testing database connection...")
        with engine.connect() as connection:
            logger.info("✓ Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'verification_tokens', 'bookings', 'forum_posts', 'forum_replies']
        created_tables = [table for table in expected_tables if table in tables]
        
        logger.info(f"✓ Database tables created successfully:")
        for table in created_tables:
            logger.info(f"  - {table}")
        
        if len(created_tables) == len(expected_tables):
            logger.info("✓ All expected tables are present")
            return True
        else:
            missing_tables = set(expected_tables) - set(created_tables)
            logger.warning(f"⚠ Some tables may be missing: {missing_tables}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        logger.exception("Full error details:")
        return False


def main():
    """Main entry point for the script."""
    logger.info("=" * 60)
    logger.info("Camargue Sailing Website - Database Initialization")
    logger.info("=" * 60)
    
    success = init_database()
    
    logger.info("=" * 60)
    if success:
        logger.info("✓ Database initialization completed successfully")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("✗ Database initialization failed")
        logger.info("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
